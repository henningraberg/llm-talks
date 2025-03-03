import click

from enums.enums import ChatRole, TextAlignment
from models.chat import Chat
from integrations.ollama_manager import OllamaManager
from database.clean_db import clean_db
from database.init_db import init_db
from simple_term_menu import TerminalMenu

from models.chat_message import ChatMessage
from models.conversation import Conversation

from rich.text import Text
from rich.console import Console
from rich.live import Live


@click.group()
def cli():
    pass


@click.command()
def set_up_conversation() -> None:
    """Set up a conversation."""
    try:
        manager = OllamaManager()
        download_models = manager.get_downloaded_models()

        assert download_models, '❌ No models downloaded. Please download a model first.'
        chats = []
        for i in range(1, 3):
            click.echo(f'Setting up LLM agent {i}')
            click.echo('Select a model:')

            terminal_menu = TerminalMenu([model.model for model in download_models.models])
            menu_entry_index = terminal_menu.show()
            model = download_models.models[menu_entry_index].model

            click.echo(f'Model: {model}')

            new_chat = Chat(default_model=model).save()
            chats.append(new_chat)

            system_message = click.prompt('Enter initial system message', type=str)
            ChatMessage(chat_id=new_chat.id, role=ChatRole.SYSTEM, content=system_message).save()

            # To get the models to start talking they both need to have empty user messages to start with.
            ChatMessage(chat_id=new_chat.id, role=ChatRole.USER, content='').save()

            click.echo('\n')

        conv = Conversation(agent_1_chat_id=chats[0].id, agent_2_chat_id=chats[1].id).save()
        click.echo(f'✅ Conversation with id {conv.id} was successfully set up!')
    except Exception as e:
        click.echo(f'❌ {e}')


@click.command()
@click.option('--conv_id', type=str, help='Conversation ID')
def show_conversation(conv_id: int) -> None:
    try:
        console = Console()
        conv = Conversation.get_one(id=conv_id)

        for message in conv.merged_chat_history:
            chat_bubble = conv.generate_chat_bubble(message)
            console.print(
                chat_bubble,
                justify=chat_bubble.renderable.title_align,
            )
    except Exception as e:
        click.echo(f'❌ {e}')
        return


@click.command()
@click.option('--conv_id', type=str, help='Conversation ID')
@click.option(
    '--interactive', default=True, type=bool, help='Run the conversation interactively by adding system messages.'
)
@click.pass_context
def run_conversation(ctx, conv_id: int, interactive: bool) -> None:
    """Run the given conversation."""
    try:
        conversation = Conversation.get_one(id=conv_id)

        keep_conversing = True

        ctx.invoke(show_conversation, conv_id=conv_id)

        messages = ChatMessage.get_multiple(
            chat_id=[conversation.agent_1_chat.id, conversation.agent_2_chat.id], role=ChatRole.ASSISTANT
        )

        # Figure out whos turn it is to answer.
        context = {'sender': conversation.agent_1_chat, 'responder': conversation.agent_2_chat}

        if messages:
            last_message = messages[-1]
            if last_message.chat_id == conversation.agent_2_chat.id:
                context = {'sender': conversation.agent_2_chat, 'responder': conversation.agent_1_chat}

        while keep_conversing:
            with Live(refresh_per_second=5) as live:
                chat_bubble = conversation.generate_empty_chat_bubble(context['sender'])
                live.update(chat_bubble)
                response = ''
                for x in OllamaManager.chat(
                    sender_agent_chat=context['sender'], responder_agent_chat=context['responder']
                ):
                    response += x
                    new_text = Text(response, justify=TextAlignment.LEFT.value)
                    chat_bubble.renderable.renderable = new_text
                    live.update(chat_bubble)

            context['sender'], context['responder'] = context['responder'], context['sender']

            if interactive:
                run_interactive_prompt(conversation)
    except Exception as e:
        click.echo(f'❌ {e}')
        return


def run_interactive_prompt(conversation: Conversation) -> None:
    options = [
        'Continue',
        'Add system message to agent 1 (right side)',
        'Add system message to agent 2 (left side)',
        'Abort',
    ]
    terminal_menu = TerminalMenu(options)
    option = None
    console = Console()
    while option != options[0]:
        menu_entry_index = terminal_menu.show()
        option = options[menu_entry_index]
        chat_message = None
        if option == options[3]:
            exit()
        elif option == options[1]:
            system_message = click.prompt('Enter system message for agent 1 (right side)', type=str)
            chat_message = ChatMessage(
                chat_id=conversation.agent_1_chat.id, role=ChatRole.SYSTEM, content=system_message
            ).save()
        elif option == options[2]:
            system_message = click.prompt('Enter system message for agent 2 (left side)', type=str)
            chat_message = ChatMessage(
                chat_id=conversation.agent_2_chat.id, role=ChatRole.SYSTEM, content=system_message
            ).save()

        if chat_message:
            chat_bubble = conversation.generate_chat_bubble(chat_message)
            console.print(
                chat_bubble,
                justify=chat_bubble.renderable.title_align,
            )


@click.command()
@click.option(
    '--model',
    type=str,
    help='Name of the model you want to download (see options at https://ollama.com/library). If you abort the progress will be saved.',
)
def download_model(model: str):
    """Download LLM model."""
    manager = OllamaManager()

    current_progress = 0
    try:
        with click.progressbar(length=1000, label=f'Downloading model {model}...') as bar:
            for progress in manager.download_model(model=model):
                if progress.completed:
                    new_progress = progress.completed
                    bar.length = progress.total
                else:
                    new_progress = current_progress + 1

                increment = new_progress - current_progress
                bar.update(increment)
                current_progress = new_progress
    except Exception as e:
        click.echo(f'❌ {e}')
        return

    click.echo(f'✅ {model} was successfully downloaded!')


@click.command()
@click.option(
    '--model',
    type=str,
    help='Name of the model you want to delete.',
)
def remove_model(model: str):
    """Remove model."""
    try:
        manager = OllamaManager()
        response = manager.delete_model(model)
        if response.status == 200:
            click.echo(f'✅ {model} was successfully removed!')
        else:
            click.echo(f'❌ {model} was not successfully removed!')
    except Exception as e:
        click.echo(f'❌ {e}')
        return


@click.command()
@click.option(
    '--conv_id',
    type=int,
    help='ID of the conversation you want to delete.',
)
def remove_conversation(conv_id: int):
    """Remove conversation."""
    try:
        conversation = Conversation.get_one(id=conv_id)
        conversation.delete()
    except Exception as e:
        click.echo(f'❌ {e}')
        return


@click.command()
def list_conversations():
    """List conversations."""
    try:
        conversations = Conversation.get_multiple()
        for conv in conversations:
            click.echo(conv.to_dict())
    except Exception as e:
        click.echo(f'❌ {e}')
        return


@click.command()
def list_models():
    """List all downloaded models."""
    try:
        downloaded_models = OllamaManager().get_downloaded_models().models
        for model in downloaded_models:
            click.echo(model.model)
    except Exception as e:
        click.echo(f'❌ {e}')


@click.command()
@click.option('--model', type=str)
def show_model(model: str):
    """Get model information."""
    try:
        response = OllamaManager().get_model_information(model)
        click.echo(response.json)
    except Exception as e:
        click.echo(f'❌ {e}')


@click.command()
def nuke_db():
    """Clean the database."""
    try:
        clean_db()
        click.echo('✅ Database tables cleared successfully!')
    except Exception as e:
        click.echo(f'❌ {e}')


@click.command()
def build_db():
    """Create the database."""
    try:
        init_db()
        click.echo('✅ Database tables created successfully!')
    except Exception as e:
        click.echo(f'❌ {e}')


# Add commands to the main CLI group
cli.add_command(download_model)
cli.add_command(list_models)
cli.add_command(remove_model)
cli.add_command(show_model)

cli.add_command(set_up_conversation)
cli.add_command(run_conversation)
cli.add_command(show_conversation)
cli.add_command(remove_conversation)
cli.add_command(list_conversations)

cli.add_command(nuke_db)
cli.add_command(build_db)

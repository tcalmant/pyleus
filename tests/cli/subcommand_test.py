import __builtin__

import mock
import testify as T

from pyleus.cli import subcommand
from pyleus.cli.subcommand import SubCommand
from pyleus.cli.subcommand import SubCommandInfo


class TestSubCommand(T.TestCase):

    def test_get_sub_command_info(self):
        with T.assert_raises(NotImplementedError):
            SubCommand.get_sub_command_info()

    def test_add_arguments(self):
        mock_parser = mock.Mock()
        with T.assert_raises(NotImplementedError):
            SubCommand.add_arguments(mock_parser)

    def test_run(self):
        mock_configs = mock.Mock()
        with T.assert_raises(NotImplementedError):
            SubCommand.run(mock_configs)

    @mock.patch.object(SubCommand, "get_sub_command_info")
    @mock.patch.object(SubCommand, "add_arguments")
    def test_add_parser(self, mock_add_arguments, mock_get_info):
        mock_subparsers = mock.Mock()
        mock_parser = mock.Mock()
        mock_subparsers.add_parser.return_value = mock_parser
        mock_get_info.return_value = SubCommandInfo(
            command_name="foo",
            usage="bar",
            description="baz",
            help_msg="qux")
        SubCommand.add_parser(mock_subparsers)
        mock_get_info.assert_called_once_with()
        mock_subparsers.add_parser.assert_called_once_with(
            "foo", usage="bar", description="baz", help="qux", add_help=False)
        mock_parser.add_argument.assert_has_calls(
            mock.call("-h", "--help", action="help",
                      help="Show this message and exit""")
        )
        mock_add_arguments.assert_called_once_with(mock_parser)
        mock_parser.set_defaults.called_once_with(
            func=SubCommand.run_subcommand)

    @mock.patch.object(subcommand, "expand_path", autospec=True)
    @mock.patch.object(subcommand, "load_configuration", autospec=True)
    @mock.patch.object(subcommand, "update_configuration", autospec=True)
    @mock.patch.object(__builtin__, "vars", autospec=True)
    @mock.patch.object(SubCommand, "run")
    def test_run_subcommand(self, mock_run, mock_vars,
                            mock_update, mock_load, mock_expand):
        mock_args = mock.Mock(config_file="foo")
        mock_expand.return_value = "bar"
        SubCommand.run_subcommand(mock_args)
        mock_expand.assert_called_once_with("foo")
        mock_load.assert_called_once_with("bar")
        mock_update.assert_called_once_with(mock_load.return_value,
                                            mock_vars(mock_args))
        mock_run.assert_called_once_with(mock_update.return_value)

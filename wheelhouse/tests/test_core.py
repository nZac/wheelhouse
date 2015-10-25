import os

from wheelhouse import core


class TestPipEnv(object):

    class MockConfig(object):
        wheelhouse_dpath = 'test'
        verbose = True

    def setup_method(self, _):

        # Clear out any potential conflicts when running these tests with TOX which sets up some
        # pip configurations we are not going to want to include.
        self.environ_cache = os.environ.copy()
        os.environ = {key: value for key, value in os.environ.iteritems() if 'PIP' not in key}

    def teardown_method(self, _):
        os.environ = self.environ_cache.copy()
        self.environ_cache = None

    def test_pip_env_returns_additional_environs(self):
        current_env_keys = os.environ.keys()
        assert len(current_env_keys) > 0

        newenv = core.pip_env(self.MockConfig())
        for key in current_env_keys:
            assert key in newenv

    def test_pip_env_uses_config_wheelhouse_dpath(self):
        newenv = core.pip_env(self.MockConfig())
        assert newenv['PIP_FIND_LINKS'] == 'test'
        assert newenv['PIP_WHEEL_DIR'] == 'test'

    def test_pip_env_uses_wheel(self):
        newenv = core.pip_env(self.MockConfig())
        assert newenv['PIP_USE_WHEEL'] == 'true'

    def test_pip_env_no_index_sets_env_var(self):
        newenv = core.pip_env(self.MockConfig())
        assert 'PIP_NO_INDEX' not in newenv

        newenv = core.pip_env(self.MockConfig(), no_index=True)
        assert 'PIP_NO_INDEX' in newenv

    def test_pip_env_pre_sets_env_var(self):
        newenv = core.pip_env(self.MockConfig())
        assert 'PIP_PRE' not in newenv

        newenv = core.pip_env(self.MockConfig(), pre=True)
        assert 'PIP_PRE' in newenv

    def test_config_controls_verbosity(self):
        newenv = core.pip_env(self.MockConfig())
        assert 'PIP_VERBOSE' in newenv

        config = self.MockConfig()
        config.verbose = False
        newenv = core.pip_env(config, pre=True)
        assert 'PIP_VERBOSE' not in newenv


class TestCallPips(object):
    """The call_pips function is not testable"""


class TestBuildFiles(object):
    """The build_files function is not testable"""


class TestBuildPackages(object):
    """The build_packages function is not testable"""


class TestInstall(object):
    """The install function is not testable"""


class TestPruneList(object):
    """The prune_list function is not testable"""

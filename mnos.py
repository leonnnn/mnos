import importlib
import sys
import subprocess

from parser import Parser
import utils
import repository
from module import Module


class Mnos:
    def __init__(self):
        self.module_queue = ModuleQueue()
        self.template_engine = utils.TemplateEngine()
        self.sysinfo = utils.SystemInfo()
        self.pkg_mgr = utils.PackageManager()

        self.config = None
        self._modules = {}

    def run(self):
        self._parse_config()
        self._load_modules()
        self._initialize_modules()
        self._run_modules()

    def _load_modules(self):
        for i in self.config["modules"]:
            print("debug:", "loading module {}…".format(i))
            self._modules[i] = importlib.import_module(
                "modules.{}".format(i)
            )

    def _initialize_modules(self):
        for i in self._modules:
            print("debug:", "initializing module {}…".format(i))
            self._modules[i] = self._modules[i].Module()

    def _run_modules(self):
        for module in self._modules.values():
            self.module_queue.enqueue(
                action=module.run,
                after=module.module_info["run_after"]
            )

    def _parse_config(self):
        parser = Parser()
        print("debug:", "parsing config…")
        with open("sample-config.txt") as f:
            self.config = parser.parse(f.read())

# TODO: use real logger instead of print()
class ModuleQueue:
    def __init__(self):
        self._events_seen = set()
        self._queue = dict()

    def enqueue(self, action, after=[]):
        """
        Schedule *action* to be called after all events in *after* have
        occurred.

        *action* is expected to be a callable object.  *after* is an
        iterable of events.  An empty list of events will cause *action*
        to be run immediately.
        """

        print("debug:", "ModuleQueue:",
              "enqueueing {} to run after {}…".format(action, after))
        # filter out events already seen
        events = set(after) - self._events_seen

        print(
            "debug:", "ModuleQueue:",
            "{} is waiting for these unseen events: {}, ".format(
                action,
                events
            ),
            end=""
        )

        if not events:
            print("running now.")
            action()
        else:
            print("enqueueing.")
            if action in self._queue:
                self._queue[action].update(events)
            else:
                self._queue[action] = events

    def fire_event(self, event):
        print("debug:", "ModuleQueue:",
              "event {} is fired.".format(event))
        self._events_seen.add(event)
        for action in self._queue.keys():
            self._queue[action].discard(event)

            print("debug:", "ModuleQueue:",
                  "checking {}… ".format(action), end="")
            if not self._queue[action]:
                print("is ready, running now.")
                action()
            else:
                print("still waiting for {}.".format(self._queue[action]))

def install_file(content, target):
    print(content)
    print("installing config file to {}…".format(target))

def execute(cmd):
    #return subprocess.check_call(cmd)
    print(" ".join(cmd))


mnos = Mnos()

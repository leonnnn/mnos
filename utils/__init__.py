import platform

import jinja2

import repository

class SystemInfo:
    """
    TODO: this is mostly wrapper for python’s platform module, do we
    really need to wrap it?
    """

    @property
    def os(self):
        return platform.system().lower()

    @property
    def platform(self):
        return platform.dist()[0].lower()

class PackageManager:
    def __init__(self):
        pass

    def request_installed(self, package):
        print("installation of {} is being requested".format(package))


class TemplateEngine:
    def render(self, *, template=None, template_file=None, options):
        if (template and template_file) or \
                (not template and not template_file):
            raise TypeError("exactly one of the template and "
                            "template_file arguments must be specified!")

        if template:
            template = jinja2.Template(template)
        elif template_file:
            with open(template_file, "r") as f:
                template = jinja2.Template(f.read())

        return template.render(options)

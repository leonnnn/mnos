import mnos

class Module(mnos.Module):
    def __init__(self, **kwargs):
        super().__init__()

    def install(self):
        mnos.pkg_mgr.request_installed(
            self.module_info["required_packages"]
        )

    def run(self):
        config = {"servers": mnos.mnos.config["system"]["ntp"]}

        result = mnos.mnos.template_engine.render(
            template_file="modules/ntp/ntp.conf.j2",
            options=config,
        )

        mnos.install_file(result, "/etc/ntp.conf")
        mnos.execute(["/etc/init.d/ntp", "start"])

    def teardown(self):
        mnos.execute(["/etc/init.d/ntp", "stop"])

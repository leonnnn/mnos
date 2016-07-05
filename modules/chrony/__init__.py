import mnos

class Module(mnos.Module):
    def __init__(self):
        super().__init__()

    def install(self):
        mnos.mnos.pkg_mgr.request_installed(
            self.module_info["required_packages"]
        )

    def run(self):
        config = {"servers": mnos.mnos.config["system"]["ntp"]}

        result = mnos.mnos.template_engine.render(
            template_file="modules/chrony/chrony.conf.j2",
            options=config,
        )

        mnos.install_file(result, "/etc/chrony.conf")
        mnos.execute(["/etc/init.d/chrony", "start"])

    def teardown(self):
        pass

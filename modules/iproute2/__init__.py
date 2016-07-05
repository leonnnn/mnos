import mnos

class Module(mnos.Module):
    def __init__(self):
        super().__init__()

    def install(self):
        self.mnos.pkg_mgr.request_installed({
            "debian-based": "iproute",
            "fedora": "iproute",
        })

    def run(self):
        interfaces = self.mnos.config["interfaces"]

        for i in interfaces:
            self._configure_interface(i, interfaces[i])

        self.mnos.module_queue.fire_event("network-started")

    def teardown(self):
        pass

    def _configure_interface(self, key, if_cfg):
            if_type, if_name = key

            opts = {
                "address": self._set_if_addr,
                "hw-id": self._set_if_hwid,
            }

            for opt in if_cfg:
                opts[opt](if_name, if_cfg[opt])

    def _set_if_addr(self, if_name, addr):
        mnos.execute(["ip", "address", "add", addr, "dev", if_name])

    def _set_if_hwid(self, if_name, hwid):
        base_cmd = ["ip", "link", "set", "dev", if_name]
        mnos.execute(base_cmd + ["down"])
        mnos.execute(base_cmd + ["address", hwid])
        mnos.execute(base_cmd + ["up"])

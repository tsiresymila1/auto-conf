from time import sleep
import os
import sys
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.worker import get_current_worker, Worker
from textual.app import CSSPathType
from textual import work
from textual.widget import Widget
from textual.driver import Driver
from textual.widgets import Button, Input, Label, Select

from textual.widgets._tabbed_content import TabbedContent, TabPane
from textual.reactive import reactive
from lib.auto import AuthConf
from lib.fpm import PHPConf
from lib.mysql import MysqlConf
from lib.nginx import Nginx

sys.path.append(os.path.join(os.path.dirname(os.path.abspath("__file__")), "lib"))


class ReactiveLabel(Widget):
    value = reactive("")

    def __init__(
        self,
        value="",
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.value = value

    def render(self) -> str:
        return self.value


class ReactiveLog(Widget):
    def __init__(
        self,
        host,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.host = host

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Access"):
                with ScrollableContainer(classes="panel", id="access-scroller"):
                    yield Label("No access log !!", id="label-access")
            with TabPane("Error"):
                with ScrollableContainer(classes="panel", id="error-scroller"):
                    yield Label("No error log !!", id="label-error")


class Footer(Widget):
    DEFAULT_CSS = """
        Footer {
            height:3 ;
            dock: bottom;
            padding: 0;
            margin: 0;
        }
        #reaload {
            background: #acacac;
            height: 2;
            width: 100%;
            border: none;
            padding: 0 0;
        }
    """

    def compose(self) -> ComposeResult:
        yield Button("RELOAD", classes="btn", id="reaload")


class AutoConfPHPApp(App[str]):
    CSS_PATH = "./lib/qui.css"
    TITLE = "Auto Conf PHP-FPM/NGINX"
    SUB_TITLE = "The most important question"
    app_dir = "/home/tsiresy/WORK/PHP/auto-php"
    ext = reactive(".local")
    index = reactive(0)

    def __init__(
        self,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.nginx = Nginx()
        self.mysql = MysqlConf(app_dir=os.path.join(os.getcwd(), "app"))
        self.autoconf = AuthConf(nginx_dir=self.nginx.dir)
        self.fpm = PHPConf(
            socket_dir=os.path.join(os.getcwd(), "run/php"),
            app_dir=os.path.join(os.getcwd(), "app"),
        )
        self.configure()

    def load(self):
        self.index = 0
        self.hosts, self.dirs, self.php_versions = self.autoconf.load_project(
            self.app_dir
        )

    def configure(self):
        self.load()
        # start php
        self.php = self.fpm.get_php_version()
        self.fpm.start_fpm()

        # start mysql
        self.mysql_version = self.mysql.mysql_version()
        if len(self.mysql_version) > 0:
            self.mysql.start(self.mysql_version[0])

        #
        php_default_version = "8.2"
        php_version = (
            php_default_version
            if php_default_version in self.php or len(self.php) == 0
            else self.php[-1]
        )
        self.nginx.configure(self.hosts, self.dirs, php_version)

    def on_mount(self) -> None:
        self.screen.styles.background = "transparent"
        self.sidebar.border_title = "List Project"
        self.sidebar.border_title_color = "#acacac"

        self.body.border_title = "Setting"
        self.body.border_title_color = "#acacac"

        self.logWidget.border_title = (
            f"Logs({self.hosts[self.index] if len(self.hosts) > 0 else ''})"
        )
        self.logWidget.border_title_color = "#acacac"

    def compose(self) -> ComposeResult:
        with Vertical() as self.body:
            with Horizontal(id="title"):
                yield Label(
                    "AUTO CONF PHP-FPM/NGINX",
                )
            with Horizontal(id="header") as self.header:
                with Horizontal(id="directory"):
                    yield Label("App directory : ", classes="label", shrink=True)
                    yield Input(self.app_dir, classes="input", id="dir-input")
                with Horizontal(id="extension"):
                    yield Label("Extension : ", classes="label", shrink=True)
                    yield Input(self.ext, classes="input")
                with Button("Save", classes="btn", id="save"):
                    pass
            with Horizontal() as self.content:
                with Container(id="sidebar", classes="focusable") as self.sidebar:
                    for h, host in enumerate(self.hosts):
                        yield Button(
                            f"{host}", classes="btn btn-sidebar", id=f"btn-host-{h}"
                        )
                    yield Footer()
                with Container(classes="reactive-body") as self.body:
                    with Horizontal(classes="reactive-body-layout"):
                        yield Label("URL:", classes="label")
                        yield ReactiveLabel(
                            self.hosts[self.index] if len(self.hosts) > 0 else "",
                            classes="reactive-label",
                            id="reactive-label-host",
                        )
                    with Horizontal(classes="reactive-body-layout"):
                        yield Label("DIR:", classes="label")
                        yield ReactiveLabel(
                            self.dirs[self.index] if len(self.hosts) > 0 else "",
                            classes="reactive-label",
                            id="reactive-label-dir",
                        )
                    with Horizontal(classes="reactive-body-layout-2"):
                        yield Label("PHP Version:", classes="label")
                        yield Select(
                            [(line, line) for line in self.php],
                            classes="select",
                            id="select-php",
                            value=self.php_versions[self.index],
                        )

                with Container(classes="reactive-log") as self.logWidget:
                    if len(self.hosts) > 0:
                        yield ReactiveLog(self.hosts[self.index])

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        input_widget: Input = self.query_one("#dir-input")
        if event.button.id == "save":
            self.app_dir = input_widget.value
            await self.update_sidenav()
        elif event.button.id == "update":
            self.configure()
            await self.update_sidenav()
        else:
            if event.button.id.startswith("btn-host-"):
                self.index = int(event.button.id.replace("btn-host-", ""))
                self.host_label: ReactiveLabel = self.query_one("#reactive-label-host")
                self.dir_label: ReactiveLabel = self.query_one("#reactive-label-dir")
                self.php_select = self.query_one("#select-php", Select)
                self.host_label.value = self.hosts[self.index]
                self.dir_label.value = self.dirs[self.index]
                self.php_select.value = self.php_versions[self.index]
                await self.update_log()

    async def update_sidenav(
        self,
    ):
        self.initHost()
        self.query_one(f"#label-access", Label).update("")
        self.query_one(f"#label-error", Label).update("")
        self.sidebar.remove_children()
        self.sidebar.mount_all(
            [
                Button(f"{host}", classes="btn btn-sidebar", id=f"btn-host-{h}")
                for h, host in enumerate(self.hosts)
            ]
            + [Footer()]
        )
        await self.update_log()

    async def update_log(self):
        self.logWidget.border_title = (
            f"Logs({self.hosts[self.index] if len(self.hosts) > 0 else ''})"
        )

    @work(exclusive=True, thread=True, name="access_worker", group="access_log")
    def readAccessLog(self):
        widget = self.query_one(f"#label-access", Label)
        scroller = self.query_one("#access-scroller", ScrollableContainer)
        worker = get_current_worker()
        while True:
            sleep(0.2)
            self.readLine(
                f"{self.nginx.dir}/logs/{self.hosts[self.index]}-access.log",
                widget,
                scroller,
                worker,
                self.index,
            )

    @work(exclusive=True, thread=True, name="error_worker", group="error_log")
    def readErrorLog(
        self,
    ):
        widget = self.query_one(f"#label-error", Label)
        scroller = self.query_one("#error-scroller", ScrollableContainer)
        worker = get_current_worker()
        while True:
            sleep(0.2)
            self.readLine(
                f"{self.nginx.dir}/logs/{self.hosts[self.index]}-error.log",
                widget,
                scroller,
                worker,
                self.index,
            )

    def readFile(self, filename):
        if os.path.isfile(filename):
            with open(filename, "r") as f:
                new_content = f.read()
                f.close()
                return new_content
        return ""

    def readLine(
        self,
        filename,
        widget: Label,
        scroller: ScrollableContainer,
        worker: Worker,
        index: int,
    ):
        content = ""
        widget.update("No content !!!")
        while True:
            new_content = self.readFile(filename)
            if new_content != content:
                if not worker.is_cancelled:
                    self.call_from_thread(widget.update, new_content)
                    scroller.scroll_end(animate=False)
                content = new_content
            sleep(0.2)
            if self.index != index:
                break

    def on_ready(self):
        self.readAccessLog()
        self.readErrorLog()


if __name__ == "__main__":
    app = AutoConfPHPApp()
    reply = app.run(headless=False)

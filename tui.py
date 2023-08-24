import pytermgui as ptg
from fpm import get_php_version

from scanner import load_project


class AutoPHP(object):
    PALETTE_LIGHT = "#03578f"
    PALETTE_MID = "#03578f"
    PALETTE_DARK = "#4D4940"
    PALETTE_DARKER = "#242321"
    manager: ptg.WindowManager
    dir = "/home/tsiresy/WORK/PHP/auto-php"
    ext = ".local"

    def __init__(self) -> None:
        ptg.tim.alias("app.text", "#cfc7b0")
        ptg.tim.alias("app.header", f"bold @{self.PALETTE_MID} #d9d2bd")
        ptg.tim.alias("app.header.fill", f"@{self.PALETTE_LIGHT}")
        ptg.tim.alias("app.title", f"bold {self.PALETTE_LIGHT}")
        ptg.tim.alias("app.button.label", f"bold @{self.PALETTE_DARK} app.text")
        ptg.tim.alias("app.button.highlight", "inverse app.button.label")
        ptg.tim.alias("app.container.highlight", "inverse app.button.label")
        ptg.tim.alias("app.footer", f"@{self.PALETTE_DARKER}")
        self.dirInput = ptg.InputField(self.dir, prompt="App directory : ")

    def reload_dir(self):
        self.hosts, self.dirs = load_project(self.dir)
        self.selected = self.hosts[0]

    def configure(self):
        ptg.boxes.SINGLE.set_chars_of(ptg.Window)
        ptg.boxes.ROUNDED.set_chars_of(ptg.Container)

        ptg.Button.styles.label = "app.button.label"
        ptg.Button.styles.highlight = "app.button.highlight"
        ptg.Button.set_char("delimiter", [" ", " "])

        ptg.Slider.styles.filled__cursor = self.PALETTE_MID
        ptg.Slider.styles.filled_selected = self.PALETTE_LIGHT

        ptg.Label.styles.value = "app.text"

        ptg.Window.styles.border__corner = "#4287f5"
        ptg.Container.styles.border__corner = self.PALETTE_DARK
        ptg.Container.styles.highlight = "app.container.highlight"

        ptg.Splitter.set_char("separator", "")

    def define_layout(self):
        layout = ptg.Layout()
        layout.add_slot("Header", height=3)
        layout.add_break()
        layout.add_slot("Header1", height=3)
        layout.add_slot("Header2", height=3, width=0.2)
        layout.add_slot("Header3", height=3, width=0.1)
        layout.add_break()
        self.manager.layout = layout
        layout.add_slot("Body right", width=0.2)
        layout.add_slot("Body")
        layout.add_break()
        layout.add_slot("Footer", height=1)
        self.manager.layout = layout
        return layout

    def update_dir(self, event):
        self.dir = self.dirInput.value
        self.manager.remove(self.sidebar)
        self.setup_sidebar()

    def setup_header(self):
        header = ptg.Window(
            f"[app.header] AUTO PHP",
            box="EMPTY",
            is_persistant=True,
            vertical_align=ptg.VerticalAlignment.CENTER,
            centered=True,
        )
        header.styles.fill = "app.header.fill"
        self.manager.add(header)

    def setup_footer(self):
        header1 = ptg.Window(
            self.dirInput,
            box="SINGLE",
            vertical_align=ptg.VerticalAlignment.CENTER,
            horizontal_align=ptg.HorizontalAlignment.LEFT,
        )
        # header1.styles.fill = "app.footer"
        self.manager.add(header1, assign="header1")

        header2 = ptg.Window(
            ptg.InputField(self.ext, prompt="Extension : "),
            box="SINGLE",
            vertical_align=ptg.VerticalAlignment.CENTER,
            horizontal_align=ptg.HorizontalAlignment.LEFT,
        )
        # header2.styles.fill = "app.footer"
        self.manager.add(header2, assign="header2")

        header3 = ptg.Window(
            ptg.Button("Save", padding=0, margin=0, onclick=self.update_dir),
            box="SINGLE",
            vertical_align=ptg.VerticalAlignment.CENTER,
            horizontal_align=ptg.HorizontalAlignment.LEFT,
        )
        # header3.styles.fill = "app.footer"
        self.manager.add(header3, assign="header3")

    def update_body(self, h, d):
        self.manager.remove(self.body)
        self.setup_body(h, d)

    def setup_sidebar(self):
        self.reload_dir()

        menu = [
            ptg.Container(
                ptg.Button(h, on_click=lambda _: self.setup_body(h, self.dir[i])),
                padding=4,
                relative_width=1,
            )
            for i, h in enumerate(self.hosts)
        ]
        self.sidebar = ptg.Window(
            *menu,
            box="SINGLE",
            width=100,
            vertical_align=ptg.VerticalAlignment.TOP,
        ).set_title("[72 bold]List project")
        self.manager.add(
            self.sidebar,
            assign="body_right",
        )

    def setup_body(self, host: str, directory: str):
        php = get_php_version()
        self.body = ptg.Window(
            ptg.Window(
                ptg.Container(
                    ptg.Container(
                        ptg.Splitter(
                            ptg.Label("URL: ", static_width=60),
                            ptg.Label(f"[72][~http://{host}] {host}"),
                            vertical_align=ptg.VerticalAlignment.CENTER,
                        ),
                        height=20,
                        box="BASIC",
                    ),
                    ptg.Container(
                        ptg.Splitter(
                            ptg.Label("PHP Version: ", static_width=60),
                            ptg.Splitter(
                                *[
                                   ptg.Splitter( ptg.Checkbox(
                                        callback=lambda e: ptg.tim.print(c),
                                        centered=True,
                                    ),ptg.Label(c, static_width=10))
                                    for c in php
                                ]
                            ),
                            vertical_align=ptg.VerticalAlignment.CENTER,
                        ),
                        height=20,
                        box="BASIC",
                    ),
                    ptg.Container(
                        ptg.Splitter(
                            ptg.Label("APP directory: ", static_width=60),
                            ptg.Label(
                                f"[78 @34;52;111][~file://{directory}]{directory}"
                            ),
                            vertical_align=ptg.VerticalAlignment.CENTER,
                        ),
                        box="BASIC",
                    ),
                    box="EMPTY",
                ),
                box="EMPTY",
                vertical_align=ptg.VerticalAlignment.TOP,
            ),
            ptg.Window(
                ptg.Container(
                    ptg.Button(
                        "UPDATE",
                        centered=True,
                        static_width=16,
                    ),
                    static_width=20,
                    parent_align=ptg.HorizontalAlignment.RIGHT,
                ),
                box="EMPTY",
                vertical_align=ptg.VerticalAlignment.BOTTOM,
                horizontal_align=ptg.HorizontalAlignment.RIGHT,
            ),
            box="SINGLE",
            vertical_align=ptg.VerticalAlignment.TOP,
            animate=False,
        )
        self.manager.add(self.body, assign="body")

    def on_quit(self):
        modal = ptg.Window(
            "[app.title] Are you sure you want to quit?",
            "",
            ptg.Container(
                ptg.Splitter(
                    ptg.Button("Yes", lambda *_: self.manager.stop()),
                    ptg.Button("No", lambda *_: self.modal.close()),
                ),
            ),
        ).center()

        modal.select(1)
        self.manager.add(modal)

    def start(self):
        self.configure()
        with ptg.WindowManager() as self.manager:
            self.define_layout()
            self.setup_header()
            self.setup_footer()
            self.setup_sidebar()
            self.setup_body(self.hosts[0], self.dir[0])

        ptg.tim.print(f"[{self.PALETTE_LIGHT}]Goodbye!\n")


if __name__ == "__main__":
    autophp = AutoPHP()
    autophp.start()

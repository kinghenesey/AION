# =============================================================
# AION UI Framework — Components
# =============================================================
# Every UI element in AION is a Component.
# Components form a tree that gets rendered to HTML.
#
# Example tree:
#   Page("Home")
#   ├── Title("Welcome")
#   ├── Text("Hello world")
#   └── Button("Click me", goto="Dashboard")

from dataclasses import dataclass, field
from typing import List, Optional


class Component:
    """Base class for all AION UI components."""
    pass


@dataclass
class Title(Component):
    """
    A large heading.
    Usage in AION:  title "Welcome to AION"
    """
    text: str

    def __repr__(self):
        return f"Title({repr(self.text)})"


@dataclass
class Text(Component):
    """
    A paragraph of text.
    Usage in AION:  text "Hello world"
    """
    content: str

    def __repr__(self):
        return f"Text({repr(self.content)})"


@dataclass
class Button(Component):
    """
    A clickable button.
    Usage in AION:
        button "Get Started":
            go Dashboard
    """
    label:  str
    goto:   Optional[str] = None
    action: Optional[str] = None

    def __repr__(self):
        return f"Button({repr(self.label)}, goto={self.goto})"


@dataclass
class Input(Component):
    """
    A text input field.
    Usage in AION:  input "Enter your name" as name
    """
    placeholder: str
    name:        str = "input"

    def __repr__(self):
        return f"Input({repr(self.placeholder)})"


@dataclass
class Image(Component):
    """
    An image.
    Usage in AION:  image "logo.png" alt "AION Logo"
    """
    src: str
    alt: str = ""

    def __repr__(self):
        return f"Image({repr(self.src)})"


@dataclass
class Divider(Component):
    """
    A horizontal divider line.
    Usage in AION:  divider
    """
    def __repr__(self):
        return "Divider()"


@dataclass
class Space(Component):
    """
    Vertical spacing.
    Usage in AION:  space
    """
    size: int = 1

    def __repr__(self):
        return f"Space({self.size})"


@dataclass
class Card(Component):
    """
    A card container with children.
    Usage in AION:
        card:
            title "Hello"
            text "World"
    """
    children: List[Component] = field(default_factory=list)

    def __repr__(self):
        return f"Card({len(self.children)} children)"


@dataclass
class Row(Component):
    """
    A horizontal row of components.
    Usage in AION:
        row:
            button "Yes"
            button "No"
    """
    children: List[Component] = field(default_factory=list)

    def __repr__(self):
        return f"Row({len(self.children)} children)"


@dataclass
class Page(Component):
    """
    A full page — the top-level UI component.
    Usage in AION:
        page Home:
            title "Welcome"
            text "Hello"
    """
    name:     str
    children: List[Component] = field(default_factory=list)

    def add(self, component: Component):
        self.children.append(component)

    def __repr__(self):
        return f"Page({self.name}, {len(self.children)} components)"


@dataclass
class UIApp(Component):
    """
    The root UI application — contains all pages.
    """
    name:  str
    pages: List[Page] = field(default_factory=list)

    def add_page(self, page: Page):
        self.pages.append(page)

    def get_page(self, name: str) -> Optional[Page]:
        for page in self.pages:
            if page.name == name:
                return page
        return None

    def __repr__(self):
        return f"UIApp({self.name}, {len(self.pages)} pages)"
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.json import JSON
from rich.markdown import Markdown
import logging

console = Console()


test = {
    'role': 'system',
    'content': 'You are a helpful assistant.'
}

test2 = """
### Test

```json
{
    "role": "system",
    "content": "You *are* a helpful assistant."
}
```
"""
panel = Markdown(test2)
panel2 = JSON.from_data(test, indent=2)

console.print(panel, panel2)   # <-- This will render correctly!

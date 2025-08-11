## user
use uv to setup and run pygame-ce from a venv
## assistant

To set up and run **pygame-ce** (the community edition of Pygame) using **[uv](https://github.com/astral-sh/uv)**, follow these steps. `uv` is a fast Python package manager that works similarly to `pip` and `pipenv`, and supports virtual environments out-of-the-box.

---

### ✅ Step-by-step Guide

#### 1. **Install `uv`** (if not already installed)
```bash
pip install uv
```
Or use a prebuilt binary from [uv's GitHub releases](https://github.com/astral-sh/uv/releases).

---

#### 2. **Create and activate a virtual environment**
```bash
uv venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

#### 3. **Install `pygame-ce` using `uv`**
```bash
uv pip install pygame-ce
```

✅ `pygame-ce` will be installed inside the virtual environment.

---

#### 4. **Verify the installation**
Run Python in the venv:
```bash
python
```
Then test Pygame:
```python
import pygame
print(pygame.__version__)
pygame.init()
```

---

#### 5. **Run a basic test script**

Create a test file, `test_game.py`:
```python
import pygame
pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pygame-CE Test")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 128, 255))
    pygame.display.flip()

pygame.quit()
```

Run it:
```bash
python test_game.py
```

---

Let me know if you want to include dependencies in a `requirements.txt` or if you want to package your game with `uv`.
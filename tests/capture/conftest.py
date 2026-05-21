"""테스트용 import 경로 설정.

`object3d` 패키지를 별도 설치 없이 import할 수 있도록
worktree의 `src/` 디렉터리를 sys.path 앞에 추가한다.
`src/object3d/`에는 __init__.py가 없으므로 PEP 420 implicit
namespace package로 동작하고, `object3d.capture`만 실제 패키지다.
"""

import sys
from pathlib import Path

# tests/capture/conftest.py -> worktree 루트 -> src
_SRC_DIR = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

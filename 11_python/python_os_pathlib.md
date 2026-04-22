# Python 파일/디렉토리 조작 (os, pathlib, shutil)

파일 시스템 조작을 위한 os, pathlib, shutil 모듈 가이드입니다.

## 목차
- [pathlib (권장)](#pathlib-권장)
- [os / os.path](#os--ospath)
- [shutil](#shutil)
- [glob 패턴](#glob-패턴)
- [권한 관리](#권한-관리)
- [실전 예제](#실전-예제)
- [요약](#요약)

---

## pathlib (권장)

### Path 객체 기본

```python
from pathlib import Path

p = Path('/etc/nginx/nginx.conf')

p.name        # 'nginx.conf'
p.stem        # 'nginx'
p.suffix      # '.conf'
p.parent      # PosixPath('/etc/nginx')
p.parents[1]  # PosixPath('/etc')
p.parts       # ('/', 'etc', 'nginx', 'nginx.conf')
p.is_absolute()  # True
```

### 경로 조합

```python
# / 연산자로 경로 결합
base = Path('/var/log')
log_file = base / 'nginx' / 'access.log'
print(log_file)  # /var/log/nginx/access.log

# 홈 디렉토리
home = Path.home()        # /home/username
cwd = Path.cwd()          # 현재 작업 디렉토리
```

### 파일/디렉토리 확인

```python
p = Path('/etc/hosts')

p.exists()      # True
p.is_file()     # True
p.is_dir()      # False
p.is_symlink()  # False
p.stat().st_size  # 파일 크기 (바이트)
```

### 파일 읽기/쓰기

```python
p = Path('output.txt')

# 쓰기
p.write_text('안녕하세요', encoding='utf-8')

# 읽기
content = p.read_text(encoding='utf-8')

# 바이너리
p.write_bytes(b'\x00\x01\x02')
data = p.read_bytes()
```

### 디렉토리 생성/삭제

```python
# 디렉토리 생성
Path('a/b/c').mkdir(parents=True, exist_ok=True)

# 파일 삭제
Path('temp.txt').unlink(missing_ok=True)

# 빈 디렉토리 삭제
Path('empty_dir').rmdir()
```

### 디렉토리 탐색

```python
p = Path('/var/log')

# 직접 하위만
for item in p.iterdir():
    print(item)

# 패턴 매칭
for conf in Path('/etc').glob('*.conf'):
    print(conf)

# 재귀 탐색
for log in Path('/var/log').rglob('*.log'):
    print(log)
```

---

## os / os.path

### 경로 처리

```python
import os

os.path.join('/var', 'log', 'syslog')   # '/var/log/syslog'
os.path.basename('/var/log/syslog')      # 'syslog'
os.path.dirname('/var/log/syslog')       # '/var/log'
os.path.splitext('file.tar.gz')          # ('file.tar', '.gz')
os.path.abspath('.')                     # 절대 경로
os.path.expanduser('~')                  # 홈 디렉토리
os.path.exists('/etc/hosts')             # True
os.path.isfile('/etc/hosts')             # True
os.path.isdir('/etc')                    # True
os.path.getsize('/etc/hosts')            # 파일 크기
```

### 디렉토리 작업

```python
os.getcwd()                    # 현재 디렉토리
os.chdir('/tmp')               # 디렉토리 이동
os.listdir('/etc')             # 파일 목록 (리스트)
os.makedirs('a/b/c', exist_ok=True)  # 재귀 생성
os.removedirs('a/b/c')        # 재귀 삭제 (빈 디렉토리만)
os.rename('old.txt', 'new.txt')

# 디렉토리 트리 순회
for root, dirs, files in os.walk('/var/log'):
    for f in files:
        print(os.path.join(root, f))
```

### 환경변수

```python
os.environ['HOME']                    # 환경변수 읽기
os.environ.get('API_KEY', 'default')  # 기본값
os.getenv('PATH')                     # get과 동일
```

---

## shutil

### 복사

```python
import shutil

# 파일 복사
shutil.copy('src.txt', 'dst.txt')        # 파일 복사 (권한 유지)
shutil.copy2('src.txt', 'dst.txt')       # 메타데이터도 복사
shutil.copyfile('src.txt', 'dst.txt')    # 내용만 복사

# 디렉토리 복사
shutil.copytree('src_dir', 'dst_dir')
shutil.copytree('src', 'dst', dirs_exist_ok=True)  # Python 3.8+
```

### 이동/삭제

```python
# 이동 (rename과 유사하지만 파일시스템 간 이동 가능)
shutil.move('src.txt', '/tmp/dst.txt')

# 디렉토리 삭제 (비어있지 않아도 삭제)
shutil.rmtree('/tmp/old_dir')

# 디스크 사용량
total, used, free = shutil.disk_usage('/')
print(f"전체: {total // (1024**3)}GB")
print(f"사용: {used // (1024**3)}GB")
print(f"여유: {free // (1024**3)}GB")
```

### 아카이브

```python
# 압축
shutil.make_archive('backup', 'zip', '/var/log')     # backup.zip
shutil.make_archive('backup', 'gztar', '/var/log')   # backup.tar.gz

# 해제
shutil.unpack_archive('backup.zip', '/tmp/extracted')
```

---

## glob 패턴

```python
import glob

glob.glob('/var/log/*.log')           # 직접 하위 .log 파일
glob.glob('/var/log/**/*.log', recursive=True)  # 재귀 탐색
glob.glob('/etc/nginx/conf.d/*.conf')
```

---

## 권한 관리

```python
import os
import stat

# 권한 변경
os.chmod('script.sh', 0o755)
os.chmod('secret.txt', stat.S_IRUSR | stat.S_IWUSR)  # 600

# 소유자 변경 (root 필요)
os.chown('file.txt', uid=1000, gid=1000)

# 권한 확인
st = os.stat('file.txt')
print(oct(st.st_mode))   # '0o100644'
print(st.st_uid)         # 소유자 UID
print(st.st_gid)         # 그룹 GID
```

### 임시 파일/디렉토리

```python
import tempfile

# 임시 파일 (자동 삭제)
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=True) as f:
    f.write('임시 데이터')
    print(f.name)  # /tmp/tmpXXXXXX.txt

# 임시 디렉토리 (자동 삭제)
with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    (tmp / 'work.txt').write_text('작업 파일')
    # with 블록 종료 시 자동 삭제
```

### 심볼릭 링크

```python
# 생성
Path('/tmp/link').symlink_to('/etc/hosts')

# 확인
p = Path('/tmp/link')
p.is_symlink()    # True
p.resolve()       # 실제 경로 반환
```

---

## 실전 예제

### 로그 로테이션

```python
from pathlib import Path
from datetime import datetime
import shutil

def rotate_logs(log_dir, max_days=7):
    log_path = Path(log_dir)
    now = datetime.now()
    for log_file in log_path.glob('*.log'):
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        age = (now - mtime).days
        if age > max_days:
            archive = log_file.with_suffix(f'.log.{mtime:%Y%m%d}')
            shutil.move(str(log_file), str(archive))
```

### 디렉토리 크기 계산

```python
def get_dir_size(path):
    total = sum(f.stat().st_size for f in Path(path).rglob('*') if f.is_file())
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} TB"
```

### 설정 파일 백업

```python
def backup_config(config_path):
    src = Path(config_path)
    if not src.exists():
        return
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dst = src.with_name(f"{src.stem}_{timestamp}{src.suffix}")
    shutil.copy2(str(src), str(dst))
    return dst
```

---

## 요약

| 모듈      | 용도                      | 권장도            |
|-----------|---------------------------|-------------------|
| `pathlib` | 경로 조작, 파일 읽기/쓰기 | ✅ 권장           |
| `os.path` | 경로 문자열 처리          | 레거시            |
| `os`      | 환경변수, 권한, 디렉토리  | 필요 시           |
| `shutil`  | 복사, 이동, 삭제, 압축    | ✅ 권장           |
| `glob`    | 패턴 매칭 파일 검색       | pathlib.glob 권장 |

**관련 문서:**
- [파일 입출력](./python_file_io.md) - 파일 읽기/쓰기
- [subprocess](./python_subprocess.md) - 외부 명령 실행
- [로깅](./python_logging.md) - 로그 파일 관리

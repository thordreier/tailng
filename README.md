# tailng

Python project: Like "tail -F", but it always follow the newest file

## Usage

### Examples

```
$ tailng
Now following testfile1 from position 108
1 4 Fri Dec 22 10:02:34 AM UTC 2023
1 5 Fri Dec 22 10:02:35 AM UTC 2023
Now following testfile2 from position 0
2 1 Fri Dec 22 10:02:36 AM UTC 2023
2 2 Fri Dec 22 10:02:37 AM UTC 2023
2 3 Fri Dec 22 10:02:38 AM UTC 2023
2 4 Fri Dec 22 10:02:39 AM UTC 2023
2 5 Fri Dec 22 10:02:40 AM UTC 2023
Now following testfile3 from position 0
3 1 Fri Dec 22 10:02:41 AM UTC 2023
3 2 Fri Dec 22 10:02:42 AM UTC 2023
3 3 Fri Dec 22 10:02:43 AM UTC 2023
```

## Install

### Install from Python Package Index

```
pip3 install tailng
```

### Install from source

```
git clone https://github.com/thordreier/tailng.git
cd tailng
git pull
pyproject-build
pip3 install $(ls dist/tailng-*-py3-none-any.whl | tail -n1) --force-reinstall
```

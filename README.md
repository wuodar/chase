# Chase

Chase appliaction.

### Description

A program that imitates a wolf chase after a sheep.
This task is implemented for 'Python programming' course at TUL.

### Authors
- Kacper Włodarczyk
- Dawid Morka

### Academic year

2020/2021

### License

MIT License

##### Create package:

- Create setup.py file with configuration of package
- Run setuptool command: 
```python setup.py sdist bdist_wheel```

##### Create virtual environment

- Run command to create venv: 
```python -m venv venv_name```
- Activate venv: 
```.\venv_name\Scripts\activate```
- Deactivate venv:
```deactivate```

##### Install package in virtual environment

- Install our package: 
```pip install -i https://test.pypi.org/simple/ chase-pkg==0.0.2```
- Import package: 
```import chase```

##### Run console application in virtual environment.

- Run command: 
```python -m chase [ARGS] ```
- List of args with description: 
```python -m chase --help ```

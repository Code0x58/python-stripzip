from setuptools import setup

setup(
    name="python-stripzip",
    use_scm_version=True,
    setup_requires=["setuptools_scm", "wheel"],
    entry_points={"console_scripts": ["stripzip = stripzip:cli"]},
    py_modules=["stripzip"],
)

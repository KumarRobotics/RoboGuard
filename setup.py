from setuptools import setup, find_packages


# todo add deps, all that
setup(
    name="roboguard",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=["openai", "spot"],
    extra_requires={"examples": ["jupyter", "jupytext"]},
)

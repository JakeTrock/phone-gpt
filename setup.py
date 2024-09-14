from setuptools import setup, find_packages

setup(
    name="phone_gpt",
    version="0.1.0",
    description="A Python server for phone GPT using FastAPI",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.94.1",
        "requests==2.28.2",
        "openai==0.27.2",
        "uvicorn==0.21.1",
        "async_timeout==4.0.2"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

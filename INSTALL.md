PoC-hasty-mode:

See [requirements.txt](./requirements.txt).

It would make sense to use `pip` here. (There's "python-pip" in package
repositories, etc.)

Using pip:

`pip install -r requirements.txt`

There's a [sample_config.py](./twidibot/sample_config.py). You need to have a
"twidibot/config.py". Create it, possibly copying from [sample_config.py]
(./twidibot/sample_config.py). Alter as appropriate.

Try not to commit "config.py" to git. It is in [.gitignore](./.gitignore) for
now.

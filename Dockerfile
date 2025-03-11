# syntax=docker/dockerfile:1
# Assembling stage.
FROM ubuntu:noble AS build

ARG python_version=3.12

# Override the standard shell start command to execute commands in “shell” form.
# https://docs.docker.com/reference/dockerfile/#shell-and-exec-form
# The `-e` option enables instant exit after an error for any unchecked command.
# A command is considered checked if it is used in a branching statement condition (e.g., `if`)
# or is the left operand of a `&&` or `|||` operator.
# The `-x` option enables printing each command to the stderr stream before it is executed. It is very useful for debugging.
# https://manpages.ubuntu.com/manpages/noble/en/man1/sh.1.html
SHELL ["/bin/sh", "-exc"]

# Install the system packages to build the project.
# Use the `apt-get` command rather than `apt` as the latter has an unstable interface.
# `libpq-dev` is a dependency of `asyncpg`, a Python package for working with the database, which will be compiled during installation.
RUN <<EOF
apt-get update --quiet
apt-get install --quiet --no-install-recommends --assume-yes \
  build-essential \
  libpq-dev \
  libmagic-dev \
  "python$python_version-dev"
EOF

# Copy the `uv` utility from the official Docker image.
# https://github.com/astral-sh/uv/pkgs/container/uv
# the `--link` option allows you to reuse a layer even if previous layers have changed.
# https://docs.docker.com/reference/dockerfile/#copy---link
COPY --link --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

# Set environment variables.
# UV_PYTHON - fixes the Python version.
# UV_PYTHON_DOWNLOADS - disables automatic downloading of missing Python versions.
# UV_PROJECT_ENVIRONMENT - specifies the path to the Python virtual environment.
# UV_LINK_MODE - changes the way packages are installed from the global cache.
# Instead of creating hard links, the package files are copied to the virtual environment directory `site-packages`.
# This is necessary for future copying of the isolated `/app` directory from the `build` stage to the final Docker image.
# UV_COMPILE_BYTECODE - enables compilation of Python files to bytecode after installation.
# https://docs.astral.sh/uv/configuration/environment/
# PYTHONOPTIMIZE - removes `assert` instructions and code that depends on the value of the `__debug__` constant,
# when compiling Python files to bytecode.
# https://docs.python.org/3/using/cmdline.html#environment-variables
ENV UV_PYTHON="python$python_version" \
  UV_PYTHON_DOWNLOADS=never \
  UV_PROJECT_ENVIRONMENT=/app \
  UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  PYTHONOPTIMIZE=1

# Copy the files needed to install dependencies without project code, since dependencies are usually changed less often than code.
COPY pyproject.toml uv.lock /warehouse_app/

# For fast local installation of dependencies, mount a cache directory where the global uv cache will be stored.
# The first call to `uv sync` creates a virtual environment and installs dependencies without the current project.
# The `--frozen` option prevents the `uv.lock` file from being updated.
RUN --mount=type=cache,destination=/root/.cache/uv <<EOF
cd /warehouse_app
uv sync \
  --no-dev \
  --no-install-project \
  --frozen
EOF

# Switch to the interpreter from the virtual environment.
ENV UV_PYTHON=$UV_PROJECT_ENVIRONMENT

# Copy project files
COPY VERSION /warehouse_app/
COPY README.md /warehouse_app/
COPY src/ /warehouse_app/src

# Set the current project.
# The `--no-editable` option disables installation of the project in “editable” mode.
# The project code is copied to the virtual environment directory `site-packages`.
RUN --mount=type=cache,destination=/root/.cache/uv <<EOF
cd /warehouse_app
sed -Ei "s/^(version = \")0\.0\.0(\")$/\1$(cat VERSION)\2/" pyproject.toml
uv sync \
  --no-dev \
  --no-editable \
  --frozen
EOF

# The final stage.
FROM ubuntu:noble AS final

# The following two arguments allow you to change the UID and GID of a Docker container user.
ARG user_id=1000
ARG group_id=1000
ARG python_version=3.12

ENTRYPOINT ["/docker-entrypoint.sh"]

# For Python applications, it is better to use the SIGINT signal, as not all frameworks (e.g. gRPC) handle the SIGTERM signal correctly.
STOPSIGNAL SIGINT
EXPOSE 8000/tcp

SHELL ["/bin/sh", "-exc"]

# Create a group and a user with the required IDs.
# If the ID value is greater than zero (exclude “root” ID) and there is already a user or group with the specified ID in the system,
# recreate the user or group with the name “app”.
RUN <<EOF
[ $user_id -gt 0 ] && user="$(id --name --user $user_id 2> /dev/null)" && userdel "$user"

if [ $group_id -gt 0 ]; then
  group="$(id --name --group $group_id 2> /dev/null)" && groupdel "$group"
  groupadd --gid $group_id app
fi

[ $user_id -gt 0 ] && useradd --uid $user_id --gid $group_id --home-dir /app app
EOF

# Install the system packages to run the project.
# Note that there are no “dev” suffixes in the package names.
RUN <<EOF
apt-get update --quiet
apt-get install --quiet --no-install-recommends --assume-yes \
  libpq5 \
  libmagic1 \
  "python$python_version"
rm -rf /var/lib/apt/lists/*
EOF

# Set environment variables.
# PATH - adds the virtual environment directory `bin` to the top of the list of directories with executables.
# This allows Python utilities to be run from any directory in the container without specifying the full file path.
# PYTHONOPTIMIZE - tells the Python interpreter to use previously compiled files from the `__pycache__` directory with the suffix `opt-1` in the name.
# PYTHONFAULTHANDLER - sets error handlers for additional signals.
# PYTHONUNBUFFERED - disables buffering for stdout and stderr streams.
# https://docs.python.org/3/using/cmdline.html#environment-variables
ENV PATH=/app/bin:$PATH \
  PYTHONOPTIMIZE=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1

COPY docker-entrypoint.sh /

RUN chmod +x /docker-entrypoint.sh

# Copy the virtual environment directory from the previous step.
COPY --link --chown=$user_id:$group_id --from=build /app /app

USER $user_id:$group_id
WORKDIR /app

# Output information about the current environment and check if the project module import works.
RUN <<EOF
python --version
python -I -m site
python -I -c 'import warehouse_app'
EOF
# Generated by rust2rpm 27
%bcond check 1

%global crate codeberg-cli

Name:           rust-codeberg-cli
Version:        0.4.9
Release:        %autorelease
Summary:        CLI Tool for codeberg similar to gh and glab

License:        AGPL-3.0-or-later
URL:            https://crates.io/crates/codeberg-cli
Source:         %{crates_source}

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel

%global _description %{expand:
CLI Tool for codeberg similar to gh and glab.}

%description %{_description}

%package     -n %{crate}
Summary:        %{summary}

%description -n %{crate} %{_description}

%files       -n %{crate}
%license LICENSE
%license LICENSE.dependencies
%doc CHANGELOG.md
%doc CONTRIBUTING.md
%doc README.md
%{_bindir}/berg
%{bash_completions_dir}/berg.bash
%{zsh_completions_dir}/_berg
%{fish_completions_dir}/berg.fish

%prep
%autosetup -n %{crate}-%{version} -p1
%cargo_prep

%generate_buildrequires
# %%cargo_generate_buildrequires

%build
# Remove offline build stuff
sed -i '/\[net\]/q' .cargo/config.toml
%cargo_build
cargo tree --workspace --edges no-build,no-dev,no-proc-macro --no-dedupe --target all --prefix none --format "{l}: {p}" | sed -e "s: ($(pwd)[^)]*)::g" -e "s: / :/:g" -e "s:/: OR :g" | sort -u > LICENSE.dependencies
BERG=./target/release/berg
$BERG completion bash > berg.bash
$BERG completion fish > berg.fish
$BERG completion zsh > _berg

%install
install -Dpm 0755 target/release/berg -t %{buildroot}%{_bindir}
install -Dpm 0644 berg.bash -t %{buildroot}%{bash_completions_dir}
install -Dpm 0644 berg.fish -t %{buildroot}%{fish_completions_dir}
install -Dpm 0644 _berg -t %{buildroot}%{zsh_completions_dir}

%if %{with check}
%check
# %%cargo_test
%endif

%changelog
%autochangelog

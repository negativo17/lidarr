%global user %{name}
%global group %{name}

Name:           lidarr
Version:        0.8.0.2042
Release:        1%{?dist}
Summary:        Automated manager and downloader for Music
License:        GPLv3
URL:            https://radarr.video/
BuildArch:      noarch

Source0:        https://github.com/%{name}/Lidarr/releases/download/v%{version}/Lidarr.develop.%{version}.linux.tar.gz
Source1:        https://raw.githubusercontent.com/lidarr/Lidarr/develop/LICENSE.md
Source2:        https://raw.githubusercontent.com/lidarr/Lidarr/develop/README.md
Source10:       %{name}.service
Source11:       %{name}.xml

BuildRequires:  firewalld-filesystem
BuildRequires:  systemd
BuildRequires:  tar

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires:       mono-core
Requires:       libmediainfo
Requires:       sqlite
Requires(pre):  shadow-utils

%description
Lidarr is a Music recored for Usenet and BitTorrent users. It can monitor
multiple RSS feeds for new music and will grab, sort and rename it. It can also
be configured to automatically upgrade the quality of files already downloaded
when a better quality format becomes available.

%prep
%autosetup -n Lidarr
cp %{SOURCE1} %{SOURCE2} .

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_prefix}/lib/firewalld/services/
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -fr * %{buildroot}%{_datadir}/%{name}

install -m 0644 -p %{SOURCE10} %{buildroot}%{_unitdir}/%{name}.service
install -m 0644 -p %{SOURCE11} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

find %{buildroot} -name "*.mdb" -delete
find %{buildroot} \( -name "*.js" -o -name "*.map" -o -name "*.config" \
    -o -name "*.css" -o -name "*.svg" -o -name "*.html" \) -exec chmod 644 {} \;

%pre
getent group %{group} >/dev/null || groupadd -r %{group}
getent passwd %{user} >/dev/null || \
    useradd -r -g %{group} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
    -c "%{name}" %{user}
exit 0

%post
%systemd_post %{name}.service
%firewalld_reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE.md
%doc README.md
%attr(750,%{user},%{group}) %{_sharedstatedir}/%{name}
%{_datadir}/%{name}
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_unitdir}/%{name}.service

%changelog
* Tue Feb 02 2021 Simone Caronni <negativo17@gmail.com> - 0.8.0.2042-1
- Update to 0.8.0.2042.

* Thu Nov 05 2020 Simone Caronni <negativo17@gmail.com> - 0.7.2.1878-1
- Update to 0.7.2.1878.

* Wed Oct 02 2019 Simone Caronni <negativo17@gmail.com> - 0.7.1.1381-1
- Update to 0.7.1.1381.

* Mon May 27 2019 Simone Caronni <negativo17@gmail.com> - 0.6.2.883-1
- Update to 0.6.2.883.

* Tue Apr 30 2019 Simone Caronni <negativo17@gmail.com> - 0.6.1.830-1
- Update to 0.6.1.830.

* Sun Dec 09 2018 Simone Caronni <negativo17@gmail.com> - 0.5.0.583-1
- Update to 0.5.0.583.

* Thu Sep 27 2018 Simone Caronni <negativo17@gmail.com> - 0.4.0.524-1
- Update to 0.4.0.524.

* Tue Jul 24 2018 Simone Caronni <negativo17@gmail.com> - 0.3.1.471-1
- Update to 0.3.1.471.

* Fri Jul 20 2018 Simone Caronni <negativo17@gmail.com> - 0.3.0.430-1
- First build.

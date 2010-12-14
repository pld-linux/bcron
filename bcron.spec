# TODO
# - pldize (sync with other cronds)
Summary:	Bruce's Cron System
Name:		bcron
Version:	0.09
Release:	0.1
License:	GPL
Group:		Applications/System
Source0:	http://untroubled.org/bcron/%{name}-%{version}.tar.gz
URL:		http://untroubled.org/bcron/
BuildRequires:	bglibs >= 1.021
Requires:	supervise-scripts >= 3.5
Requires:	ucspi-unix
Conflicts:	dcron
Conflicts:	fcron
Conflicts:	vixie-cron
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Bruce's Cron System.

%prep
%setup -q

%build
echo "%{__cc} %{rpmcflags}" > conf-cc
echo "%{__cc} %{rpmldflags}" > conf-ld
echo "%{_bindir}" > conf-bin
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
%{__make} install \
	install_prefix=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_mandir}/man{1,8}
cp -a bcron-{exec,sched,spool,start,update}.8 $RPM_BUILD_ROOT%{_mandir}/man8
cp -a bcrontab.1 $RPM_BUILD_ROOT%{_mandir}/man1

install -d $RPM_BUILD_ROOT/var/service/bcron-{sched/log,spool,update}
install -p bcron-sched.run $RPM_BUILD_ROOT/var/service/bcron-sched/run
install -p bcron-sched-log.run $RPM_BUILD_ROOT/var/service/bcron-sched/log/run
install -p bcron-spool.run $RPM_BUILD_ROOT/var/service/bcron-spool/run
install -p bcron-update.run $RPM_BUILD_ROOT/var/service/bcron-update/run
chmod +t $RPM_BUILD_ROOT/var/service/bcron-sched

install -d $RPM_BUILD_ROOT/var/log/bcron

install -d $RPM_BUILD_ROOT/var/spool/cron/{crontabs,tmp}
mkfifo $RPM_BUILD_ROOT/var/spool/cron/trigger

install -d $RPM_BUILD_ROOT%{_sysconfdir}/bcron
install -d $RPM_BUILD_ROOT/etc/cron.d

%clean
rm -rf $RPM_BUILD_ROOT

%pre
grep -q '^cron:' /etc/group \
|| groupadd -r cron
grep -q '^cron:' /etc/passwd \
|| useradd -r -d /var/spool/cron -s /sbin/nologin -g cron cron

%post
PATH="$PATH:%{_prefix}/local/bin"
if [ "$1" = 1 ]; then
  for svc in bcron-sched bcron-spool bcron-update; do
	if ! [ -e /service/$svc ]; then
	  svc-add $svc
	fi
  done
else
  for svc in bcron-sched bcron-spool bcron-update; do
	svc -t /service/$svc
  done
fi

%preun
if [ "$1" = 0 ]; then
  for svc in bcron-sched bcron-spool bcron-update; do
	if [ -L /service/$svc ]; then
	  svc-remove $svc
	fi
  done
fi

%files
%defattr(644,root,root,755)
%doc ANNOUNCEMENT COPYING NEWS README
%doc bcron.texi bcron.html
%config %dir %{_sysconfdir}/bcron
%config %dir /etc/cron.d

%attr(755,root,root) %{_bindir}/*
%{_mandir}/*/*

/var/service/*

%attr(700,cron,cron) %dir /var/spool/cron
%attr(700,cron,cron) %dir /var/spool/cron/crontabs
%attr(700,cron,cron) %dir /var/spool/cron/tmp
%attr(600,cron,cron)      /var/spool/cron/trigger

%attr(700,root,root) %dir /var/log/bcron

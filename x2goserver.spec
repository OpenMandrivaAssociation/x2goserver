# This is work in progress
# not finished yet, so please don't complain about strange things
# I just wanted to have it in svn, so it's revisioned
# obgr_seneca

%define x2golibdir %{_libdir}/x2go

Name:		x2goserver
Version:	4.0.0.0
Release:	%mkrel 5
Summary:	The server-side core of X2go
License:	GPLv2+
Group:		Networking/Remote access
Url:		https://wiki.x2go.org/doku.php
Source0:	http://code.x2go.org/releases/source/%{name}/%{name}-%{version}.tar.gz
Source1:	%{name}.service
BuildRequires:	man2html-core
Requires:	openssh-server
Requires:	openssh-clients
Requires:	lsof
Requires:	perl-Config-Simple
Requires:	makepasswd
Requires:	xauth
Requires:	sshfs-fuse
# x2go / nx dependencies
Requires:	x2goagent
Requires:	xcomp
Requires:	xcompext
Requires:	nxproxy
Requires:	nxX11
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Suggests:	%{name}-database

%description
x2go is a "server based computing environment" combining the advantages of
different existing solutions.
The x2goserver package provides the server-side core of X2go.

%package sqlite
Summary:	Virtual package for using %{name} with sqlite
Group:		Networking/Remote access
Requires:	sqlite3-tools
Requires:	perl-DBD-SQLite
Provides:	%{name}-database = %{version}-%{release}

%description sqlite
This is a virtual package that just provides the neccesary packages needed to
run x2go with a default sqlite database setup.

%package postgresql
Summary:	Virtual package for using %{name} with a postgresql database
Group:		Networking/Remote access
Requires:	postgresql-server
Requires:	perl-DBD-Pg
Provides:	%{name}-database = %{version}-%{release}

%description postgresql
This is a virtual package that just provides the neccesary packages needed to
run x2go with a postgresql setup. Note, you can also run x2go with a remote
postgresql setup.

%prep
%setup -q

# Set path
find -type f | xargs sed -i -r -e '/^LIBDIR=/s,/lib/,/%{_lib}/,'
sed -i -e 's,/lib/,/%{_lib}/,' x2goserver/bin/x2gopath
# Don't try to be root
sed -i -e 's/-o root -g root//' */Makefile
# Perl pure_install
sed -i -e 's/perl install/perl pure_install/' Makefile

%build
export LC_ALL=C
%make PREFIX=%{_prefix} CFLAGS="%optflags"

%install
export LC_ALL=C
%makeinstall_std PREFIX=%{_prefix} \
    INSTALL_DIR="install -d -m 755" \
    INSTALL_FILE="install -m 644" \
    INSTALL_PROGRAM="install -m 755"
rm -f %{buildroot}%{_sysconfdir}/x2go/Xsession.d

mkdir -p %{buildroot}%{_unitdir}
install -m0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

cat  > README.install.urpmi << EOF

DATABASE SETUP
-----------------

You need either an sqlite or a postgresql database for running x2go.
If you want to run x2go just on a single server, sqlite is sufficient, for
running x2go on a multi server setup, postgresql is required.

 $ x2godbadmin --createdb


DEFAULT: SQLite setup
------------------------

This variant is the default X2go database setup. The X2go database keeps track
of running/suspended/finished X2go sessions, mounted devices, etc. If you use
SQLite as DB backend, X2go will run on one single server.

For multi-X2goServer support use the PostgreSQL setup variant of X2go server. 
All files should be present for this setup. If not, please report it as a bug.


ALTERNATIVE: PostgreSQL setup
--------------------------------

This variant is for a setup of x2goserver that uses a PostgreSQL database 
backend...

The exact installation of x2goserver with PostgreSQL support is described
here: http://wiki.x2go.org/doku.php/wiki:advanced:multi-node:x2goserver-pgsql

LOCAL FOLDER SHARING
-----------------------

Users that shall be able to use X2go's local folder sharing functionality 
(via sshfs) have to be members of your server system's ,,fuse'' group

 $ usermod -a -G fuse <username>


PRINTING
-----------

Also users that shall be able to send print jobs to client-side printers have
to be members of the server-side ,,fuse'' group (see above).

As X2go printing setups can be rather versatile, details on X2go printing are 
explained in the project wiki:
http://wiki.x2go.org/doku.php/doc:installation:printing


INITSCRIPT
------------

Until now, there is none, has to be written from scratch and will follow soonest.
The server can be started by the command x2gocleansessions& as root in the meanwhile.
EOF

find %{buildroot} -name .placeholder -delete
mkdir -p %{buildroot}%{_localstatedir}/lib/x2go
mkdir -p %{buildroot}%{_localstatedir}/spool/x2goprint

%pre
%_pre_useradd x2gouser %{_localstatedir}/lib/x2go /bin/false
%_pre_useradd x2goprint %{_localstatedir}/spool/x2goprint /bin/false

%post
chown x2gouser:x2gouser %{_localstatedir}/lib/x2go
chown x2goprint:x2goprint %{_localstatedir}/spool/x2goprint
# Initialize the session database
[ ! -f %{_localstatedir}/lib/x2go/x2go_sessions ] && %{_sbindir}/x2godbadmin --createdb || :

%postun
%_postun_userdel x2gouser
%_postun_userdel x2goprint

%files sqlite

%files postgresql

%files
%doc README.install.urpmi
%doc %{_mandir}/man*/x2go*
%dir %{_localstatedir}/lib/x2go
%dir %{_localstatedir}/spool/x2goprint
%{_datadir}/x2go
%{_bindir}/x2gobasepath
%{_bindir}/x2gocmdexitmessage
%{_bindir}/x2gofeature
%{_bindir}/x2gofeaturelist
%{_bindir}/x2gogetapps
%{_bindir}/x2gogetservers
%{_bindir}/x2golistdesktops
%{_bindir}/x2golistmounts
%{_bindir}/x2golistsessions
%{_bindir}/x2gomountdirs
%attr(2755,root,x2goprint) %{_bindir}/x2goprint
%{_bindir}/x2goresume-session
%{_bindir}/x2goruncommand
%{_bindir}/x2goserver-run-extensions
%{_bindir}/x2gosessionlimit
%{_bindir}/x2gosetkeyboard
%{_bindir}/x2goshowblocks
%{_bindir}/x2gostartagent
%{_bindir}/x2gosuspend
%{_bindir}/x2gosuspend-agent
%{_bindir}/x2gosuspend-session
%{_bindir}/x2goterminate
%{_bindir}/x2goterminate-session
%{_bindir}/x2goumount-session
%{_bindir}/x2goversion
%{_bindir}/x2gopath
%{_sbindir}/x2go*
%{_sysconfdir}/X11/Xsession.options
%dir %{_sysconfdir}/x2go
%{_sysconfdir}/x2go/Xresources
%{_sysconfdir}/x2go/Xsession
%{_sysconfdir}/x2go/Xsession.options
%config(noreplace) %{_sysconfdir}/x2go/x2goserver.conf
%{_sysconfdir}/x2go/x2gosql/sql
%{_sysconfdir}/x2go/x2go_logout
%{_sysconfdir}/x2go/x2go_logout.d/010_userscripts.sh
%{_sysconfdir}/x2go/x2goagent.options
%{_unitdir}/%{name}.service
%dir %{x2golibdir}
%{x2golibdir}/x2gochangestatus
%{x2golibdir}/x2gocreatesession
%{x2golibdir}/x2godbwrapper.pm
%{x2golibdir}/x2gogetagent
%{x2golibdir}/x2gogetdisplays
%{x2golibdir}/x2gogetports
%{x2golibdir}/x2gogetstatus
%{x2golibdir}/x2goinsertport
%{x2golibdir}/x2goinsertsession
%{x2golibdir}/x2golistsessions_sql
%{x2golibdir}/x2gologlevel
%{x2golibdir}/x2gologlevel.pm
%{x2golibdir}/x2gormport
%{x2golibdir}/x2goresume
%{x2golibdir}/extensions
%attr(2755,root,x2gouser) %{x2golibdir}/x2gosqlitewrapper
%{x2golibdir}/x2gosqlitewrapper.pl
%{x2golibdir}/x2gosuspend-agent
%{x2golibdir}/x2gosyslog

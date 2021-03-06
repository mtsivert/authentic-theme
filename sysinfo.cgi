#
# Authentic Theme 9.5.0 (https://github.com/qooob/authentic-theme)
# Copyright 2015 Ilia Rostovtsev <programming@rostovtsev.ru>
# Licensed under MIT (https://github.com/qooob/authentic-theme/blob/master/LICENSE)
#

BEGIN { push( @INC, ".." ); }
use WebminCore;
&ReadParse();
&init_config();

do "authentic-theme/authentic-lib.cgi";

&load_theme_library();
( $hasvirt, $level, $hasvm2 ) = get_virtualmin_user_level();
%text = &load_language($current_theme);
%text = ( &load_language('virtual-server'), %text );

&header($title);
print '<div id="wrapper" class="page" data-notice="'
    . (
    ( -f $root_directory . '/authentic-theme/update' && $level == 0 )
    ? _post_install()
    : '0'
    ) . '">' . "\n";
print '<div class="container">' . "\n";
print
    '<div id="system-status" class="panel panel-default" style="margin-bottom: 5px">'
    . "\n";
print '<div class="panel-heading">' . "\n";
print '<h3 class="panel-title">' . &text('body_header0') . (
    ( $level != 2 && $level != 3 && &foreign_available("webmin") )
    ? '<a href="/?updated" target="_top" data-href="'
        . $gconfig{'webprefix'}
        . '/webmin/edit_webmincron.cgi" data-refresh="system-status" class="btn btn-success pull-right" style="margin:-6px -11px;color: white"><i class="fa fa-refresh"></i></a>
        <button type="button" class="btn btn-primary" style="display: none; visibility: hidden" data-toggle="modal" data-target="#update_notice"></button>'
    : ''
) . '</h3>' . "\n";

print '</div>';
print '<div class="panel-body">' . "\n";

# Get system info to show
my @info = &list_combined_system_info();

# Print System Warning
print_sysinfo_warning(@info);

if ( $level == 0 ) {

    # Ask status module for collected info
    &foreign_require("system-status");
    $info = &system_status::get_collected_info();

    # Circle Progress Container
    print '<div class="row" style="margin: 0;">' . "\n";
    $col_width = &get_col_num( $info, 12 );

    # CPU Usage
    if ( $info->{'cpu'} ) {
        @c    = @{ $info->{'cpu'} };
        $used = $c[0] + $c[1] + $c[3];
        &print_progressbar_colum( 6, $col_width, $used, 'CPU' );
    }

    # MEM e VIRT Usage
    if ( $info->{'mem'} ) {
        @m = @{ $info->{'mem'} };
        if ( @m && $m[0] ) {
            $used = ( $m[0] - $m[1] ) / $m[0] * 100;
            &print_progressbar_colum( 6, $col_width, $used, 'MEM' );
        }
        if ( @m && $m[2] ) {
            $used = ( $m[2] - $m[3] ) / $m[2] * 100;
            &print_progressbar_colum( 6, $col_width, $used, 'VIRT' );
        }
    }

    # HDD Usage
    if ( $info->{'disk_total'} ) {
        ( $total, $free ) = ( $info->{'disk_total'}, $info->{'disk_free'} );
        $used = ( $total - $free ) / $total * 100;
        &print_progressbar_colum( 6, $col_width, $used, 'HDD' );
    }
    print '</div>' . "\n";

    # Info table
    print '<table class="table table-hover">' . "\n";

    # Hostname Info
    $ip
        = $info && $info->{'ips'}
        ? $info->{'ips'}->[0]->[0]
        : &to_ipaddress( get_system_hostname() );
    $ip = " ($ip)" if ($ip);
    $host = &get_system_hostname() . $ip;
    if ( &foreign_available("net") ) {
        $host
            = '<a href="'
            . $gconfig{'webprefix'}
            . '/net/list_dns.cgi">'
            . $host . '</a>';
    }
    &print_table_row( &text('body_host'), $host );

    # Operating System Info
    if ( $gconfig{'os_version'} eq '*' ) {
        $os = $gconfig{'real_os_type'};
    }
    else {
        $os = $gconfig{'real_os_type'} . ' ' . $gconfig{'real_os_version'};
    }
    &print_table_row( &text('body_os'), $os );

    # Webmin version
    &print_table_row( &text('body_webmin'), &get_webmin_version() );

    # Virtualmin version
    if ($hasvirt) {
        my %vinfo = &get_module_info("virtual-server");
        my $is_virtual_server_gpl = $vinfo{'version'} =~ /gpl/;
        if ($is_virtual_server_gpl eq '1')
        {
            $vs_license = '0';

        }
        else {
            $vs_license = '1';
        }

        $__virtual_server_version = $vinfo{'version'};
        $__virtual_server_version =~ s/.gpl//igs;
        print_table_row(
            $text{'right_virtualmin'},
            $__virtual_server_version . " " . (
                $vs_license eq '0'
                ? ''
                : 'Pro'

                    . (
                    ( $vs_license eq '1' )
                    ? ' <a class="btn btn-default btn-xs btn-hidden hidden" data-toggle="tooltip" data-placement="top" title="'
                        . $text{'right_vlcheck'}
                        . '" style="margin-left:1px;padding:0 6px; line-height: 12px; height:15px;font-size:11px" href="'
                        . $gconfig{'webprefix'}
                        . '/virtual-server/licence.cgi"><i class="fa fa-refresh" style="padding-top:1px"></i></a>'
                    : ''
                    )

            )
        );
    }

    # Cloudmin version
    if ($hasvm2) {
        my %vinfo = &get_module_info("server-manager");
        $is_server_manager_gpl = $vinfo{'version'} =~ /gpl/;
        if ($is_server_manager_gpl eq '1')
        {
            $vm2_license = '0';

        }
        else {
            $vm2_license = '1';
        }

        $__server_manager_version = $vinfo{'version'};
        $__server_manager_version =~ s/.gpl//igs;
        print_table_row(
            $text{'right_vm2'},
            $__server_manager_version . " " . (
                $vm2_license eq '0'
                ? ''
                : 'Pro'

                    . (
                    ( $vm2_license eq '1' )
                    ? ' <a class="btn btn-default btn-xs btn-hidden hidden" data-toggle="tooltip" data-placement="top" title="'
                        . $text{'right_vlcheck'}
                        . '" style="margin-left:1px;padding:0 6px; line-height: 12px; height:15px;font-size:11px" href="'
                        . $gconfig{'webprefix'}
                        . '/server-manager/licence.cgi"><i class="fa fa-refresh" style="padding-top:1px"></i></a>'
                    : ''
                    )

            )
        );
    }

    # Theme version/updates
    # Define installed version
    open my $authentic_installed_version, '<',
        $root_directory . "/authentic-theme/VERSION.txt";
    my $installed_version = <$authentic_installed_version>;
    close $authentic_installed_version;

    # Define remote version
    use LWP::Simple;
    my $remote_version
        = get(
        'http://rostovtsev.ru/.git/authentic-theme/VERSION.txt'
        );
    open( FILENAME, '<', \$remote_version );

    # Trim spaces
    $installed_version =~ s/\s+$//;
    $remote_version =~ s/\s+$//;

    # Parse response message
    if ( version->parse($remote_version)
        <= version->parse($installed_version) )
    {
        $authentic_theme_version
            = '<a href="https://github.com/qooob/authentic-theme" target="_blank">'
            . $text{'authentic_theme'} . '</a> '
            . $installed_version
            . '<div class="modal fade" id="update_notice" tabindex="-1" role="dialog" aria-labelledby="update_notice_label" aria-hidden="true">
                  <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                        <h4 class="modal-title" id="update_notice_label">'
            . $text{'theme_update_notice'} . '</h4>
                      </div>
                      <div class="modal-body">
                        <h4>Version 9.5.0 (February 8, 2015)</h4>
                        <ul>
                            <li>Added <code>dataTables</code> to <em>Software Package Updates</em>, as it\'s useful to sort packages by <em>name/description/status/source</em></li>
                            <li>Added font <code>Roboto</code> in the package and set as default. Font now is local, because <em>Google</em> is blocked in some countries <a href="https://github.com/qooob/authentic-theme/issues/80" target="_blank">(Issue 80)</a></li>
                            <li>Added <code>Hotkey</code> - <em>double</em> <code>Shift</code> for dismissing right side loader</li>
                            <li>Added custom <code>styles</code> and <code>scripts</code> injector. Now you can apply custom <em>styles/scripts</em> to the theme, which will be preserved upon updates. Read the <a href="https://github.com/qooob/authentic-theme#how-do-i-load-custom-styles" target="_blank">Manual</a> for more details</li>
                            <li>Added <code>brand</code> icons for <em>Webmin/Virtualmin/Cloudmin</em> switches (thanks to <em>Joe Cooper</em> for it)</li>
                            <li>Added <code>left menu</code> dependency updates, upon some triggers happening on the right frame</li>
                            <li>Added <code>extended panels</code> on <em>System Information</em> page, like <em>Quotas</em>, <em>Status</em>, <em>IP address allocation</em> and et cetera</li>
                            <li>Added Perl <code>error message</code>, explaining how to make the theme work, if it\'s downloaded from <em>GitHub</em> as <em>.zip</em> <a href="https://github.com/qooob/authentic-theme/issues/85" target="_blank">(Issue 85)</a></li>
                            <li>Fixed missing option <code>create sub-servers</code>, when clicking on <em>Create Virtual Server</em> link, on theme very first load <a href="https://github.com/qooob/authentic-theme/issues/96" target="_blank">(Issue 96)</a></li>
                            <li>Fixed <code>sticking out</code> <em>long text</em> in the left menu in some languages (Russian, French, Polish and some other) <a href="https://github.com/qooob/authentic-theme/issues/95" target="_blank">(Issue 95)</a></li>
                            <li>Fixed <code>stuck loader</code>, when going to <em>Webmin Scheduled Functions</em> <a href="https://github.com/qooob/authentic-theme/issues/86" target="_blank">(Issue 86)</a></li>

                        </ul>
                        <h4 style="margin-top:20px">'
            . $text{'theme_development_support'} . '</h4>
                        Thank you for using <a target="_blank" href="https://github.com/qooob/authentic-theme"><kbd style="background:#5cb85c">'
            . $text{'authentic_theme'}
            . '<kbd></a>. Overall development of this theme has already passed the stage of <kbd>240</kbd> hours.
                          While I am glad to provide <em>Authentic</em> Theme for free, it would mean a world to me, if you send me a <a target="_blank" class="badge fa fa-paypal" style="font-size: 11px; background-color: #5bc0de;" href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&lc=us&business=programming%40rostovtsev%2eru&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHostedGuest"> donation</a>.
                          It doesn\'t matter how big or small your donation is. I appreciate all donations. Each donation will excite future development and improve your everyday experience, while working with the theme.
                          <br>
                          <br>
                          Don\'t forget nor be lazy to post to <a class="badge fa fa-github" style="font-size: 11px; background-color: #337ab7;" target="_blank" href="https://github.com/qooob/authentic-theme"> GitHub</a> found bugs.<br>
                          <br>
                          Please rate/comment theme presentation on <a class="badge label-danger fa fa-youtube" style="font-size: 11px; background-color: #c9302c;" target="_blank" href="http://www.youtube.com/watch?v=gfuPFuGpyv8"> YouTube</a> channel.
                      </div>
                    </div>
                  </div>
               </div>';
    }
    else {
        $authentic_theme_version
            = '<a href="https://github.com/qooob/authentic-theme" target="_blank">'
            . $text{'authentic_theme'} . '</a> '
            . $installed_version . '. '
            . $text{'theme_update_available'} . ' '
            . $remote_version
            . '&nbsp;&nbsp;&nbsp;<div class="btn-group">'
            . '<a class="btn btn-xs btn-success authentic_update" style="padding:0 8px; height:21px" href="'
            . $gconfig{'webprefix'}
            . '/webmin/edit_themes.cgi"><i class="fa fa-refresh">&nbsp;</i>'
            . $text{'theme_update'} . '</a>'
            . '<a class="btn btn-xs btn-info" style="padding:0 8px; height:21px" target="_blank" href="https://github.com/qooob/authentic-theme/blob/master/CHANGELOG.md"><i class="fa fa-pencil-square-o">&nbsp;</i>'
            . $text{'theme_changelog'} . '</a>'
            . '<a class="btn btn-xs btn-warning" style="padding:0 8px; height:21px" target="_blank" href="https://rostovtsev.ru/.git/authentic-theme/authentic-theme-latest.wbt.gz"><i class="fa fa-download">&nbsp;</i>'
            . $text{'theme_download'} . '</a>'
            . '<a class="btn btn-xs btn-default" style="padding:0 8px; height:21px" target="_blank" href="https://github.com/qooob/authentic-theme#donation"><i class="fa fa-rub">&nbsp;</i>'
            . $text{'theme_donate'} . '</a>'
            . '</div>';
    }
    &print_table_row( $text{'theme_version'}, $authentic_theme_version );

    #System Time
    use Time::Local;
    $tm = localtime( time() );
    if ( &foreign_available("time") ) {
        $tm = '<a href=' . $gconfig{'webprefix'} . '/time/>' . $tm . '</a>';
    }
    &print_table_row( &text('body_time'), $tm );

    # Kernel and CPU Info
    if ( $info->{'kernel'} ) {
        &print_table_row(
            &text('body_kernel'),
            &text(
                'body_kernelon',                $info->{'kernel'}->{'os'},
                $info->{'kernel'}->{'version'}, $info->{'kernel'}->{'arch'}
            )
        );
    }

    # CPU Type and cores
    if ( $info->{'load'} ) {
        @c = @{ $info->{'load'} };
        if ( @c > 3 ) {
            &print_table_row( $text{'body_cpuinfo'},
                &text( 'body_cputype', @c ) );
        }
    }

    # Temperatures Info (if available)
    if ( $info->{'cputemps'} ) {
        foreach my $t ( @{ $info->{'cputemps'} } ) {
            $cputemp
                .= 'Core '
                . $t->{'core'} . ': '
                . int( $t->{'temp'} )
                . '&#176;C<br>';
        }
        &print_table_row( $text{'body_cputemps'}, $cputemp );
    }
    if ( $info->{'drivetemps'} ) {
        foreach my $t ( @{ $info->{'drivetemps'} } ) {
            my $short = $t->{'device'};
            $short =~ s/^\/dev\///;
            my $emsg;
            if ( $t->{'errors'} ) {
                $emsg
                    .= ' (<span class="text-danger">'
                    . &text( 'body_driveerr', $t->{'errors'} )
                    . "</span>)";
            }
            elsif ( $t->{'failed'} ) {
                $emsg
                    .= ' (<span class="text-danger">'
                    . &text('body_drivefailed')
                    . '</span>)';
            }
            $hddtemp
                .= $short . ': '
                . int( $t->{'temp'} )
                . '&#176;C<br>'
                . $emsg;
        }
        &print_table_row( $text{'body_drivetemps'}, $hddtemp );
    }

    # System uptime
    &foreign_require("proc");
    my $uptime;
    my ( $d, $h, $m ) = &proc::get_system_uptime();
    if ($d) {
        $uptime = &text( 'body_updays', $d, $h, $m );
    }
    elsif ($m) {
        $uptime = &text( 'body_uphours', $h, $m );
    }
    elsif ($m) {
        $uptime = &text( 'body_upmins', $m );
    }
    if ($uptime) {
        if ( &foreign_available("init") ) {
            $uptime
                = '<a href='
                . $gconfig{'webprefix'}
                . '/init/>'
                . $uptime . '</a>';
        }
        &print_table_row( $text{'body_uptime'}, $uptime );
    }

    # Running processes
    if ( &foreign_check("proc") ) {
        @procs = &proc::list_processes();
        $pr    = scalar(@procs);
        if ( &foreign_available("proc") ) {
            $pr
                = '<a href='
                . $gconfig{'webprefix'}
                . '/proc/>'
                . $pr . '</a>';
        }
        &print_table_row( $text{'body_procs'}, $pr );
    }

    # Load averages
    if ( $info->{'load'} ) {
        @c = @{ $info->{'load'} };
        if (@c) {
            &print_table_row( $text{'body_cpu'}, &text( 'body_load', @c ) );
        }
    }

    # Real memory details
    &print_table_row(
        $text{'body_real'},
        &text(
            'body_used',
            nice_size( ( $m[0] ) * 1000 ),
            nice_size( ( $m[0] - $m[1] ) * 1000 )
        )
    );

    # Virtual memory details
    &print_table_row(
        $text{'body_virt'},
        &text(
            'body_used',
            nice_size( ( $m[2] ) * 1000 ),
            nice_size( ( $m[2] - $m[3] ) * 1000 )
        )
    );

    # Local disk space
    &print_table_row(
        $text{'body_disk'},
        &text(
            'body_used_and_free',
            nice_size( $info->{'disk_total'} ),
            nice_size( $info->{'disk_free'} ),
            nice_size( $info->{'disk_total'} - $info->{'disk_free'} )
        )
    );

    # Package updates
    if ( $info->{'poss'} ) {
        @poss = @{ $info->{'poss'} };
        @secs = grep { $_->{'security'} } @poss;
        if ( @poss && @secs ) {
            $msg = &text( 'body_upsec', scalar(@poss), scalar(@secs) );
        }
        elsif (@poss) {
            $msg = &text( 'body_upneed', scalar(@poss) );
        }
        else {
            $msg = $text{'body_upok'};
        }
        if ( &foreign_available("package-updates") ) {
            my $updates_num  = $msg;
            my $updates_text = $msg;
            $updates_num =~ s/[^0-9]//g;
            $updates_text =~ s/\d//g;
            $message
                = '<a href="'
                . $gconfig{'webprefix'}
                . '/package-updates/index.cgi?mode=updates">'
                . '<i class="badge badge-danger">'
                . $updates_num
                . '</i>&nbsp;'
                . $updates_text
                . '</a> <a href="/?updated" target="_top" data-href="'
                . $gconfig{'webprefix'}
                . '/webmin/edit_webmincron.cgi" data-refresh="system-status package-updates" class="btn btn-primary btn-xs btn-hidden hidden" style="margin-left:4px;color: white;padding:0 12px; line-height: 12px; height:15px; font-size:11px"><i class="fa fa-refresh" style="padding-top:1px"></i></a>';
        }
        &print_table_row( $text{'body_updates'}, $message );
    }
    print '</table>' . "\n";

    # Webmin notifications
    if ( &foreign_check("webmin") ) {
        &foreign_require( "webmin", "webmin-lib.pl" );
        my @notifs = &webmin::get_webmin_notifications();
        if (@notifs) {
            print '<div class="panel-footer">' . "\n";
            print "<center>\n", join( "<hr>\n", @notifs ), "</center>\n";
            print '</div>' . "\n";
        }

        # print scalar(@notifs);
    }

    print '</div>';    # Panel Body
    print '</div>';    # Panel Heading

    print_extended_sysinfo(@info);

}
elsif ( $level == 2 ) {

    # Domain owner
    # Show a server owner info about one domain
    $ex = virtual_server::extra_admin();
    if ($ex) {
        $d = virtual_server::get_domain($ex);
    }
    else {
        $d = virtual_server::get_domain_by( "user", $remote_user, "parent",
            "" );
    }

    print '<table class="table table-hover">' . "\n";

    &print_table_row( $text{'right_login'}, $remote_user );

    &print_table_row( $text{'right_from'}, $ENV{'REMOTE_HOST'} );

    if ($hasvirt) {
        my $__virtual_server_version = $virtual_server::module_info{'version'};
        $__virtual_server_version =~ s/.gpl//igs;
        &print_table_row( $text{'right_virtualmin'},
            $__virtual_server_version);
    }
    else {
        &print_table_row( $text{'right_virtualmin'}, $text{'right_not'} );
    }

    $dname
        = defined(&virtual_server::show_domain_name)
        ? &virtual_server::show_domain_name($d)
        : $d->{'dom'};
    &print_table_row( $text{'right_dom'}, $dname );

    @subs = ( $d, virtual_server::get_domain_by( "parent", $d->{'id'} ) );
    @reals = grep { !$_->{'alias'} } @subs;
    @mails = grep { $_->{'mail'} } @subs;
    ( $sleft, $sreason, $stotal, $shide )
        = virtual_server::count_domains("realdoms");
    if ( $sleft < 0 || $shide ) {
        &print_table_row( $text{'right_subs'}, scalar(@reals) );
    }
    else {
        &print_table_row( $text{'right_subs'},
            text( 'right_of', scalar(@reals), $stotal ) );
    }

    @aliases = grep { $_->{'alias'} } @subs;
    if (@aliases) {
        ( $aleft, $areason, $atotal, $ahide )
            = virtual_server::count_domains("aliasdoms");
        if ( $aleft < 0 || $ahide ) {
            &print_table_row( $text{'right_aliases'}, scalar(@aliases) );
        }
        else {
            &print_table_row( $text{'right_aliases'},
                text( 'right_of', scalar(@aliases), $atotal ) );
        }
    }

    # Users and aliases info
    $users = virtual_server::count_domain_feature( "mailboxes", @subs );
    ( $uleft, $ureason, $utotal, $uhide )
        = virtual_server::count_feature("mailboxes");
    $msg = @mails ? $text{'right_fusers'} : $text{'right_fusers2'};
    if ( $uleft < 0 || $uhide ) {
        &print_table_row( $msg, $users );
    }
    else {
        &print_table_row( $msg, text( 'right_of', $users, $utotal ) );
    }

    if (@mails) {
        $aliases = virtual_server::count_domain_feature( "aliases", @subs );
        ( $aleft, $areason, $atotal, $ahide )
            = virtual_server::count_feature("aliases");
        if ( $aleft < 0 || $ahide ) {
            &print_table_row( $text{'right_faliases'}, $aliases );
        }
        else {
            &print_table_row( $text{'right_faliases'},
                text( 'right_of', $aliases, $atotal ) );
        }
    }

    # Databases
    $dbs = virtual_server::count_domain_feature( "dbs", @subs );
    ( $dleft, $dreason, $dtotal, $dhide )
        = virtual_server::count_feature("dbs");
    if ( $dleft < 0 || $dhide ) {
        &print_table_row( $text{'right_fdbs'}, $dbs );
    }
    else {
        &print_table_row( $text{'right_fdbs'},
            text( 'right_of', $dbs, $dtotal ) );
    }

    if ( !$sects->{'noquotas'}
        && virtual_server::has_home_quotas() )
    {
        # Disk usage for all owned domains
        $homesize = virtual_server::quota_bsize("home");
        $mailsize = virtual_server::quota_bsize("mail");
        ( $home, $mail, $db ) = virtual_server::get_domain_quota( $d, 1 );
        $usage = $home * $homesize + $mail * $mailsize + $db;
        $limit = $d->{'quota'} * $homesize;
        if ($limit) {
            &print_table_row( $text{'right_quota'},
                text( 'right_of', nice_size($usage), &nice_size($limit) ),
                3 );
        }
        else {
            &print_table_row( $text{'right_quota'}, nice_size($usage), 3 );
        }
    }

    if (  !$sects->{'nobw'}
        && $virtual_server::config{'bw_active'}
        && $d->{'bw_limit'} )
    {
        # Bandwidth usage and limit
        &print_table_row(
            $text{'right_bw'},
            &text(
                'right_of',
                &nice_size( $d->{'bw_usage'} ),
                &text(
                    'edit_bwpast_' . $virtual_server::config{'bw_past'},
                    &nice_size( $d->{'bw_limit'} ),
                    $virtual_server::config{'bw_period'}
                )
            ),
            3
        );
    }

    print '</table>' . "\n";

    # New features for domain owner
    #show_new_features(0);

    print '</div>';    # Panel Body
    print '</div>';    # Panel Heading

    print_extended_sysinfo(@info);
}
elsif ( $level == 3 ) {
    print '<table class="table table-hover">' . "\n";

    # Host and login info
    &print_table_row( &text('body_host'), &get_system_hostname() );

    # Operating System Info
    if ( $gconfig{'os_version'} eq '*' ) {
        $os = $gconfig{'real_os_type'};
    }
    else {
        $os = $gconfig{'real_os_type'} . ' ' . $gconfig{'real_os_version'};
    }
    &print_table_row( &text('body_os'), $os );

    # Usermin version
    &print_table_row( &text('body_usermin'), &get_webmin_version() );

    # Theme version/updates
    # Define installed version
    open my $authentic_installed_version, '<',
        $root_directory . "/authentic-theme/VERSION.txt";
    my $installed_version = <$authentic_installed_version>;
    close $authentic_installed_version;

    # Define remote version
    use LWP::Simple;
    my $remote_version
        = get(
        'http://rostovtsev.ru/.git/authentic-theme/VERSION.txt'
        );
    open( FILENAME, '<', \$remote_version );

    # Trim spaces
    $installed_version =~ s/\s+$//;
    $remote_version =~ s/\s+$//;

    # Parse response message
    if ( version->parse($remote_version)
        <= version->parse($installed_version) )
    {
        $authentic_theme_version
            = '' . $text{'authentic_theme'} . ' ' . $installed_version;
    }
    else {
        $authentic_theme_version
            = ''
            . $text{'authentic_theme'} . ' '
            . $installed_version . '. '
            . $text{'theme_update_available'} . ' '
            . $remote_version
            . '&nbsp;&nbsp;<a class="btn btn-xs btn-info" style="padding:0 8px; height:21px" target="_blank" href="https://github.com/qooob/authentic-theme/blob/master/CHANGELOG.md">'
            . ''
            . $text{'theme_changelog'} . '</a>';
    }
    &print_table_row( $text{'theme_version'}, $authentic_theme_version );

    #System Time
    $tm = localtime( time() );
    if ( &foreign_available("time") ) {
        $tm = '<a href=' . $gconfig{'webprefix'} . '/time/>' . $tm . '</a>';
    }
    &print_table_row( &text('body_time'), $tm );

    # Disk quotas
    if ( &foreign_installed("quota") ) {
        &foreign_require( "quota", "quota-lib.pl" );
        $n     = &quota::user_filesystems($remote_user);
        $usage = 0;
        $quota = 0;
        for ( $i = 0; $i < $n; $i++ ) {
            if ( $quota::filesys{ $i, 'hblocks' } ) {
                $quota += $quota::filesys{ $i, 'hblocks' };
                $usage += $quota::filesys{ $i, 'ublocks' };
            }
            elsif ( $quota::filesys{ $i, 'sblocks' } ) {
                $quota += $quota::filesys{ $i, 'sblocks' };
                $usage += $quota::filesys{ $i, 'ublocks' };
            }
        }
        if ($quota) {
            $bsize = $quota::config{'block_size'};
            print '<tr>' . "\n";
            print '<td><strong>'
                . $text{'body_uquota'}
                . '</strong></td>' . "\n";
            print '<td>'
                . &text(
                'right_out',
                &nice_size( $usage * $bsize ),
                &nice_size( $quota * $bsize )
                ),
                '</td>' . "\n";
            print '</tr>' . "\n";
            print '<tr>' . "\n";
            print '<td></td>' . "\n";
            print '<td>' . "\n";
            print '<div class="progress">' . "\n";
            $used = $usage / $quota * 100;
            print
                '<div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="'
                . $used
                . '" aria-valuemin="0" aria-valuemax="100" style="width: '
                . $used . '%">' . "\n";
            print '</div>' . "\n";
            print '</div>' . "\n";
            print '</td>' . "\n";
            print '</tr>' . "\n";
        }
    }
    print '</table>' . "\n";

    print '</div>';    # Panel Body
    print '</div>';    # Panel Heading

    print_extended_sysinfo(@info);
}

# End of page
# print '</div>'; # Panel Body
# print '</div>'; # Panel Heading

print '</div>' . "\n";

&footer();

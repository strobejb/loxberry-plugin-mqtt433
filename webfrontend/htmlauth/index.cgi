#!/usr/bin/perl

# This is a sample Script file
# It does not much:
#   * Loading configuration
#   * including header.htmlfooter.html
#   * and showing a message to the user.
# That's all.

use File::HomeDir;
use CGI qw/:standard/;
use Config::Simple;
use Cwd 'abs_path';
use IO::Socket::INET;
use HTML::Entities;
use String::Escape qw( unquotemeta );
use warnings;
use strict;
no strict "refs"; # we need it for template system

my  $home = File::HomeDir->my_home;
our $lang;
my  $installfolder;
my  $cfg;
my  $conf;
our $psubfolder;
our $template_title;
our $namef;
our $value;
our %query;
our $phrase;
our $phraseplugin;
our $languagefile;
our $languagefileplugin;
our $cache;
our $savedata;
our $MSselectlist;
our $txpin;
our $enabled;
our $Enabledlist;
our $pidmsg;

# ---------------------------------------
# Read Settings
# ---------------------------------------
$cfg             = new Config::Simple("$home/config/system/general.cfg");
$installfolder   = $cfg->param("BASE.INSTALLFOLDER");
$lang            = $cfg->param("BASE.LANG");


print "Content-Type: text/html\n\n";

# ---------------------------------------
# Parse URL
# ---------------------------------------
foreach (split(/&/,$ENV{"QUERY_STRING"}))
{
  ($namef,$value) = split(/=/,$_,2);
  $namef =~ tr/+/ /;
  $namef =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $query{$namef} = $value;
}

# ---------------------------------------
# Set parameters coming in - GET over POST
# ---------------------------------------
if ( !$query{'txpin'} )   { if ( param('txpin')  ) { $txpin = quotemeta(param('txpin'));         } 
else { $txpin = $txpin;  } } else { $txpin = quotemeta($query{'txpin'});   }

if ( !$query{'enabled'} )   { if ( param('enabled')  ) { $enabled = quotemeta(param('enabled'));         } 
else { $enabled = $enabled;  } } else { $enabled = quotemeta($query{'enabled'});   }

# ---------------------------------------
# Figure out in which subfolder we are installed
# ---------------------------------------
$psubfolder = abs_path($0);
$psubfolder =~ s/(.*)\/(.*)\/(.*)$/$2/g;


# ---------------------------------------
# Save settings to config file
# ---------------------------------------
if (param('savedata')) {
	$conf = new Config::Simple("$home/config/plugins/$psubfolder/mqtt433.cfg");

	if ($enabled ne 1) { $enabled = 0 }

	$conf->param('MQTT433.TXPIN', unquotemeta($txpin));
	$conf->param('MQTT433.ENABLED', unquotemeta($enabled));
	
	$conf->save();
}


# ---------------------------------------
# Parse config file
# ---------------------------------------
$conf = new Config::Simple("$home/config/plugins/$psubfolder/mqtt433.cfg");
$txpin = encode_entities($conf->param('MQTT433.TXPIN'));
$enabled = encode_entities($conf->param('MQTT433.ENABLED'));


# ---------------------------------------
# Set Enabled / Disabled switch
# ---------------------------------------
if ($enabled eq "1") {
	$Enabledlist = '<option value="0">No</option><option value="1" selected>Yes</option>\n';
} else {
	$Enabledlist = '<option value="0" selected>No</option><option value="1">Yes</option>\n';
}


# Init Language
	# Clean up lang variable
	$lang         =~ tr/a-z//cd; $lang         = substr($lang,0,2);
  # If there's no language phrases file for choosed language, use german as default
		if (!-e "$installfolder/templates/system/$lang/language.dat") 
		{
  		$lang = "de";
	}
	# Read translations / phrases
		$languagefile 			= "$installfolder/templates/system/$lang/language.dat";
		$phrase 						= new Config::Simple($languagefile);
		$languagefileplugin = "$installfolder/templates/plugins/$psubfolder/$lang/language.dat";
		$phraseplugin 			= new Config::Simple($languagefileplugin);



# PID of daemon
my $pname = "REPLACELBPBINDIR/mqtt433.py"; 
my $pid = `pgrep -f $pname`;

if([ $pid gt 0] ) {
  $pidmsg = "Running: (PID $pid)";
}
else {
  $pidmsg = "Not Running";
}

# Title
$template_title = $phrase->param("TXT0000") . ": MQTT433";

# ---------------------------------------
# Load header and replace HTML Markup <!--$VARNAME--> with perl variable $VARNAME
# ---------------------------------------
open(F,"$installfolder/templates/system/$lang/header.html") || die "Missing template system/$lang/header.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

# ---------------------------------------
# Load content from template
# ---------------------------------------
open(F,"$installfolder/templates/plugins/$psubfolder/$lang/content.html") || die "Missing template $lang/content.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

# ---------------------------------------
# Load footer and replace HTML Markup <!--$VARNAME--> with perl variable $VARNAME
# ---------------------------------------
open(F,"$installfolder/templates/system/$lang/footer.html") || die "Missing template system/$lang/header.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

exit;

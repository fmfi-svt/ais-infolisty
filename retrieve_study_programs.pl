#! /usr/bin/perl -w
use strict;
use File::Temp qw/ tempfile tempdir /;
use File::Basename;
use FindBin qw($Bin);

my $usage = "
$0 season target_directory
";

my $season = shift or die $usage;
my $fakulta = "FMFI";
my $target_directory = shift or die $usage;
my $xmlurl = "https://ais2.uniba.sk/repo2/repository/default/ais/studijneplany";
my $xmlurlpodprogramy = "https://ais2.uniba.sk/repo2/repository/default/ais/studijneplanypodprogramov";

my $tempdir = tempdir( CLEANUP=>1 );

download_data("sk");
download_data("en");
process_data("sk");
process_data("en");


sub process_data {
    my ($lang) = @_;

    my $ultimatesource = "$tempdir/$fakulta/xml_files_$lang";
    my $ultimatetarget = "$target_directory/$season/$lang";
    print STDERR "Processing $lang into $ultimatetarget...\n";

    my_run("mkdir -p $ultimatetarget");

    my @allfiles = glob("$ultimatesource/*.xml");
    foreach my $f (@allfiles) {
	my ($basename) = fileparse($f,".xml");
	my_run("$Bin/studijne-programy.pl $ultimatesource/$basename.xml $ultimatetarget/sp_$basename.html $ultimatetarget/sp_$basename-vyucujuci.html $Bin/portal-vs/portal-vs.tsv",0);
    }
    
}


sub download_data {
    my ($lang) = @_;

    print STDERR "Retrieving data for language $lang...\n";

    my $LANG = uc $lang;
    my $datadir="$tempdir/$fakulta";
    my $filelist="$datadir/files_$lang.txt";
    my $xmldir="$datadir/xml_files_$lang";

    my $lynxcmd = "lynx --dump \"$xmlurl/$season/$fakulta/$LANG/\" | awk '/http/{print \$2}' | grep xml > \"$filelist\"";
    # my $wgetcmd = "wget -N -q -i \"$filelist\" -P \"$xmldir\"";


    my_run("mkdir -p $datadir");
    my_run("mkdir -p $xmldir");
    my_run($lynxcmd);
    open OUT,">>$filelist";
    print OUT "$xmlurlpodprogramy/$season/$fakulta/$LANG/1MXX.xml\n";
    print OUT "$xmlurlpodprogramy/$season/$fakulta/$LANG/2MXX.xml\n";
    close OUT;

    open IN,"<$filelist";
    while (my $file = <IN>) {
	## download file by file because wget has memory leak
	chomp $file;
	my $wgetcmd = "wget -N -q \"$file\" -P \"$xmldir\"";
	my_run($wgetcmd,0);
    }
    close IN;
}

sub my_run
{
    my ($run, $die) = @_;
    if(!defined($die)) { $die = 1; }

    my $short = substr($run, 0, 20);

    print STDERR $run, "\n";
    my $res = system($run);
    if($res<0) {
        die "Error in program '$short...' '$!'";
    }
    if($? && $die) {
        my $exit  = $? >> 8;
        my $signal  = $? & 127;
        my $core = $? & 128;

        die "Error in program '$short...' "
            . "(exit: $exit, signal: $signal, dumped: $core)\n\n ";
    }
}

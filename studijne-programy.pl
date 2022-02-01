#! /usr/bin/perl -w
use strict;
use XML::Simple;
use Data::Dumper;
use utf8;
use Unicode::Collate;

binmode STDOUT,":utf8";
binmode STDERR,":utf8";


my $usage = "
$0 <xml_subor> <html_subor> <prehlad-ucitelov>
";

my $xmlfile = shift or die $usage;
my $htmlfile = shift or die $usage;
my $prehlad = shift;
my $portal = shift;
my %portalvsindex;
if ($portal) {
    citaj_portalvs()
}

my $pocetStlpcov = 6;

my %vyucujuciprogramu;

my $ref = XMLin($xmlfile) or die "Cannot read XML file $xmlfile";
my $out;
open( $out, ">:encoding(UTF-8)",$htmlfile) or die "Cannot open $htmlfile for writing";

print $out 
"<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<html>
<head>
<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />
<style type=\"text/css\">
           body {font-family: serif; max-width: 80em;}
            h1 {
                font-size: 110%;
                text-align: left;
            }
            table {width: 100%; border-collapse: collapse;}
            table td {padding: 0.3em; border: thin solid black;}
            p, dl {margin: 0;}
            h1 + p {margin-bottom: 1.5em;}
            dl dt {font-weight: bold; float: left; clear: left; margin-right: 0.5em;}
            dt:after {content: \":\";}

            table th {text-align: left; padding-top: 20px; }

</style>
</head>
<body>";

my $sp = $ref->{'studijnePlany'}{'studijnyPlan'};

hlavicka_sp($out,$sp);

my $bloky = stiahni_bloky($sp);

print $out "<p><table>\n";

foreach my $blok (@{$bloky}) {
    vypis_blok($out,$blok);
}

print $out "</table>";
print $out "</body></html>";
close $out;

if ($prehlad) {
    open $out,">:encoding(UTF-8)", $prehlad or die "Cannot open $prehlad for writing!";

    print $out "<html><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /><body>\n";

    my $uc = Unicode::Collate->new();

    print $out "<h1>Prehľad vyučujúcich profilových predmetov</h1>\n";

    foreach my $v ($uc->sort(keys(%vyucujuciprogramu))) {
	next unless defined $vyucujuciprogramu{$v}{'profpredmety'};
	print $out join("; ","<b>".$vyucujuciprogramu{$v}{'meno'}."</b>",$vyucujuciprogramu{$v}{'email'},soe($vyucujuciprogramu{$v}{'portal'}));
	print $out "<br>\n";
	print $out "<i>",join("; ",@{$vyucujuciprogramu{$v}{'profpredmety'}}),"</i><br>\n";
    }


    print $out "<h1>Prehľad vyučujúcich</h1>\n";
    
    foreach my $v ($uc->sort(keys(%vyucujuciprogramu))) {
	print $out join("; ","<b>".$vyucujuciprogramu{$v}{'meno'}."</b>",$vyucujuciprogramu{$v}{'email'},soe($vyucujuciprogramu{$v}{'portal'}));
	print $out "<br>\n";
	print $out "<i>",join("; ",@{$vyucujuciprogramu{$v}{'predmety'}}),"</i><br>\n";
    }

    print $out "</body></html>";
    close $out;
}




sub hlavicka_sp {
    my ($out,$ref) = @_;

    print $out "<h1>".$ref->{'co'}{'nazov'}."</h1>\n";

    my $odbory = aoe($ref->{'studijneOdbory'}{'studijnyOdbor'});
    foreach my $odbor (@{$odbory}) {
        print $out "<p><b>študijný odbor:</b> ",$odbor->{'nazov'};
	my $garanti = aoe($odbor->{'garanti'}{'garant'});
	foreach my $garant (@{$garanti}) {
	    print $out "<br><b>",$garant->{'typGaranta'},":</b> ",
	    $garant->{'meno'};
	}
    }

    print $out "<p><b>akademický rok:</b> ",$ref->{'akademickyRok'};

}

sub stiahni_bloky {
    my ($ref) = @_;

    my @bloky;
 
    my $castisp = aoe($ref->{'castiStudijnehoPlanu'}{'cast'});
    foreach my $cast (@{$castisp}) {
	my $nazov_casti = $cast->{'nazov'};
	my $poznamkypredcastou = join("<br>",@{aoe($cast->{'obmedzenie'}{'poznamkyPred'}{'poznamkaPred'})});
	my $poznamkyzacastou = join("<br>",@{aoe($cast->{'obmedzenie'}{'poznamkyZa'}{'poznamkaZa'})});

	my $sutypy; my $typyvyucby;
	if (exists $cast->{'typyVyucby'}) {
	    $typyvyucby = aoe($cast->{'typyVyucby'}{'typ'});
	    $sutypy = 1;
	} else {
	    $typyvyucby = [ $cast ];
	    $sutypy = 0;
	}
	
	foreach my $typ (@{$typyvyucby}) {
	    my $nazov_typu = $typ->{'nazov'};
	    my $skratka_typu = $typ->{'skratka'};
	    my $poznamkypredtypom = join("<br>",@{aoe($typ->{'obmedzenie'}{'poznamkyPred'}{'poznamkaPred'})});
	    my $poznamkyzatypom = join("<br>",@{aoe($typ->{'obmedzenie'}{'poznamkyZa'}{'poznamkaZa'})});

	    my $dalsie_bloky = aoe($typ->{'bloky'}{'blok'});
	    foreach my $blok (@{$dalsie_bloky}) {
		if ($sutypy) {
		    $blok->{'comment'} = "$nazov_casti / $nazov_typu";
		} else {
		    $blok->{'comment'} = "$nazov_casti";
		}
		$blok->{'ppc'} = $poznamkypredcastou;
		$blok->{'pzc'} = $poznamkyzacastou;
		if ($sutypy) {
		    $blok->{'skratka_typu'} = $skratka_typu;
		    $blok->{'ppt'} = $poznamkypredtypom;
		    $blok->{'pzt'} = $poznamkyzatypom;
		}
		push (@bloky,$blok);
	    }
	}
    }

    return \@bloky;
}

sub vypis_blok {
    my ($out,$ref) = @_;

    my $skratka = $ref->{'skratka'};
    my $st = $ref->{'skratka_typu'};
    return if ($skratka =~ /MXX/) && !($st eq "A") && !($xmlfile =~ /MXX/);
    
    my $kredit = $ref->{'obmedzenie'}{'kredit'};
    my $nazov = $ref->{'nazov'};
    my $blokypredmetov = aoe($ref->{'predmety'});
    my $predmety;
    foreach my $bp (@{$blokypredmetov}) {
	my $cp = aoe($bp->{'predmet'});
	push(@{$predmety},@{$cp});
    }
    my $poznamkypred = join("<br>",@{aoe($ref->{'obmedzenie'}{'poznamkyPred'}{'poznamkaPred'})});
    my $poznamkyza = join("<br>",@{aoe($ref->{'obmedzenie'}{'poznamkyZa'}{'poznamkaZa'})});
    my $comment = $ref->{'comment'};
    my $ppc = $ref->{'ppc'};
    my $pzc = $ref->{'pzc'};
    my $ppt = $ref->{'ppt'};
    my $pzt = $ref->{'pzt'};

    print $out "<tr><th colspan = $pocetStlpcov>$skratka: $nazov</th></tr>\n";
    print $out "<tr><td colspan = $pocetStlpcov>
                  $comment<br>";
    print $out "minimálne $kredit kreditov<br>" if ($kredit);
    print $out "$ppc<br>" if ($ppc);
    print $out "$ppt<br>" if ($ppt);
    print $out "$poznamkypred</td></tr>\n";

    foreach my $predmet (@{$predmety}) {
	vypis_predmet($out,$predmet);
    }

    print $out "<tr><td colspan = $pocetStlpcov>";
    print $out "$pzc<br>" if ($pzc);
    print $out "$pzt<br>" if ($pzt);
    print $out "$poznamkyza</td></tr>\n";

}

sub citaj_portalvs {
    open my $portalf,"<:encoding(UTF-8)",$portal;

    my %count;
    while (my $line = <$portalf>) {
	chomp $line;
	my @parts = split "\t",$line;
	$count{$parts[0]}++;
	if ($count{$parts[0]} > 1) {	    
	    $portalvsindex{$parts[0]} = "!" unless $portalvsindex{$parts[0]} eq $parts[1];
	} else {
	    $portalvsindex{$parts[0]}=$parts[1];
	}
    }

    close $portalf;
}

sub daj_vyucujucich {
    my ($ref,$predmet,$jeprof) = @_;

    my $vyucujuci = "";
    my $sep = "";
    foreach my $vref (@{$ref}) {
	my $email = soe($vref->{'pridelenyEmail'});
	my $link = "";
	if ($email =~ /^(.+)\@uniba\.sk$/) {
	    $link = "https://sluzby.fmph.uniba.sk/ludia/$1";
	}

	my $osoba = soe($vref->{'meno'})." ".soe($vref->{'priezvisko'});
	if ($link) {
	    $osoba = "<a href=\"$link\">$osoba</a>";
	}
	
	$vyucujuci .= $sep.$osoba;
	$sep = ", ";

	# vybuduj index vyucujucich
	my $index = soe($vref->{'priezvisko'}).', '.soe($vref->{'meno'});
	my $portalindex = lc(soe($vref->{'priezvisko'}).' '.soe($vref->{'meno'}));
	$vyucujuciprogramu{$index}{'meno'} = soe($vref->{'plneMeno'});
	$vyucujuciprogramu{$index}{'url'} = $link;
	$vyucujuciprogramu{$index}{'email'} = $email;
	push @{$vyucujuciprogramu{$index}{'predmety'}}, $predmet;
	push @{$vyucujuciprogramu{$index}{'profpredmety'}}, $predmet if $jeprof;	
	if (defined $portalvsindex{$portalindex}) {
	    $vyucujuciprogramu{$index}{'portal'}="https://portalvs.sk".$portalvsindex{$portalindex};
	}
    }

    return $vyucujuci;

}

sub jeprofilovy {
    my ($ref) = @_;

    my $priznaky = aoe($ref->{'priznak'});
    foreach my $p (@{$priznaky}) {
	if ($p eq "P") {
	    return "P";
	}
    }

    return "";
}

sub vypis_predmet {
    my ($out,$ref) = @_;

    my ($kod,$subor) = uprav_kod($ref->{'skratka'});
    my $nazov = $ref->{'nazov'};
    my $jeprof = jeprofilovy($ref);
    # my $vyucujuci = soe($ref->{'vyucujuci2'});
    my $vyucujuci = daj_vyucujucich(aoe($ref->{'vyucujuciAll'}{'vyucujuci'}),$nazov,$jeprof);
    my $konanie = soe($ref->{'rocnik'}).'/'.soe($ref->{'semester'});
    my $rozsah = soe($ref->{'rozsah'});
    my $aktualnost = soe($ref->{'aktualnost'});
    my $kreditov = $ref->{'kredit'}."kr";
    my $prerekvizity = soe($ref->{'podmienujucePredmety'});
    $prerekvizity =~ s/([\w\.\+]+)\/(\S+)\/(\d+)/$2\/$3/g;
    
    print $out
	"<tr><td>$kod</td><td>$jeprof$aktualnost</td>
        <td width=60%><a href=\"$subor\">$nazov</a>"; 
    print $out "<i> - $vyucujuci</i>" if ($vyucujuci);
    print $out "<br>Prerekvizity: $prerekvizity" if ($prerekvizity);
    print $out "</td>
             <td>$konanie</td><td>$rozsah</td><td>$kreditov</td></tr>\n";
}

sub uprav_kod {
    my ($kod) = @_;

    if ($kod =~ /^([^\/]*FMFI[^\/]*)\/([^\/]*)\/(\d*)$/) {
	return ("$2/$3","$2_$3.html");
    } else {
	my $subor = $kod;
	$subor =~ s/\//_/g;
	return ($kod,$subor);
    }
}

sub soe {
    # string or empty
    my ($what) = @_;

    if (ref $what eq ref {}) {
	return "";
    } elsif (defined $what) {
	return $what;
    } else {
	return "";
    }
}

sub aoe {
    # array or else
    my ($ref) = @_;

    my @newref;
  
    if (ref $ref eq ref []) {
	return $ref;
    } elsif (defined $ref) {
	push(@newref,$ref);
	return \@newref;
    } else {
	return \@newref;
    }
}

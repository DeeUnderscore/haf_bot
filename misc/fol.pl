#!/usr/bin/perl

if (not exists $ARGV[0]) {
	print "No file specified\n";
	exit(1);
}

open(fh, '<', $ARGV[0]) or die $!;
my (@convos);
my $convo = '';

while(<fh>){
	if(/<(\S*)>\s!o (.*)/) {
		if ($convo != '') { $convo += "\n" }
		$convo = $convo . "<$1> $2\n";
	}
	elsif(/omegle>> (.*)/) {
		if ($convo != '') { $convo += "\n" }
		$convo = $convo . '<*stranger*> ' . $1 . "\n";
	}
	elsif(/\[omegle\] Disconn/) {
		push(@convos, $convo);
		$convo = '';
	}
}

my $counter = 1;

foreach(@convos){
	print "\n\n***\nConversation " . $counter . "\n\n";
	print $_;
	$counter++
}

__END__

=head1 fol.pl

fol.pl - Format Omegle Logs

Takes an xchat-wdk-formatted log file and spits out only the Omegle bot
explicit mode exchanges

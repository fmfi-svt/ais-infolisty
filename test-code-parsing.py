 # coding=utf8
import utils

print utils.parse_code(u"FMFI.KAMŠ+KAI/1-EFM-380/00");
print utils.parse_code(u"PriF.KBCh/N-bCBI-303/10");
print utils.parse_code(u"PriF.KBCh/N-bCBI-303/3ecf/10");
print utils.parse_code(u"alebo");

print utils.replace_codes(u"FMFI.KAMŠ/1-MAT-282/00 alebo FMFI.KAMŠ/2-INF-175/15", add_links=True);
print utils.replace_codes(u"FMFI.KI+KAI/2-INF-262/15 - Bezpečnosť IT infraštruktúry  a FMFI.KI/2-INF-178/15 - Kryptológia (1)  a FMFI.KI/2-INF-223/15 - Riadenie IT bezpečnosti  a FMFI.KI/2-INF-183/15 - Počítačové siete (2)  a FMFI.KI/2-INF-176/15 - UNIX pre administrátorov  a FMFI.KI/2-INF-224/15 - Teória informácie a teória kódovania (1)  a FMFI.KI/2-INF-225/15 - Teória informácie a teória kódovania (2)");

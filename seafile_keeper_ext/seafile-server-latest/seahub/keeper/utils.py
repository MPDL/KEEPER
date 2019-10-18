# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import re

from seahub.invitations.models import Invitation

# List from http://colab.mpdl.mpg.de/mediawiki/Max_Planck_email_domains
# Format: Institutsname<Tab>Ort<Tab>eMail domain<Tab>Kommentar
EMAIL_DOMAIN_LIST = '''Bibliotheca Hertziana - Max-Planck-Institut für Kunstgeschichte	Rom	biblhertz.it
Deutsches Klimarechenzentrum	Hamburg	dkrz.de
Ernst Strüngmann Institute (ESI) for Neuroscience in Cooperation with Max-Planck-Society	Frankfurt am Main	esi-frankfurt.de	nicht Teil des MPG e.V. (RUFSI)
Forschungszentrum caesar (center of advanced european studies and research)	Bonn	caesar.de	nicht Teil des MPG e.V. (RUFSI)
Friedrich-Miescher-Laboratorium für biologische Arbeitsgruppen in der Max-Planck-Gesellschaft	Tübingen	tuebingen.mpg.de
Fritz-Haber-Institut der Max-Planck-Gesellschaft	Berlin	fhi-berlin.mpg.de
Generalverwaltung	München	gv.mpg.de
GWD Göttingen	Göttingen	gwdg.de
Halbleiterlabor der Max-Planck-Gesellschaft	München	hll.mpg.de
Haus der Astronomie	Heidelberg	hda-hd.de
Kunsthistorisches Institut in Florenz - Max-Planck-Institut	Florenz	khi.fi.it
Max Planck Computing and Data Facility	Garching	rzg.mpg.de
Max Planck Digital Library	München	mpdl.mpg.de
Max Planck Florida Institute for Neuroscience	FL 33458, USA	maxplanckflorida.org	nicht Teil des MPG e.V. (RUFSI)
Max Planck Florida Institute for Neuroscience	FL 33458, USA	mpfi.org	nicht Teil des MPG e.V. (RUFSI)
Max Planck Foundation for International Peace and the Rule of Law		mpfpr.de
Max Planck Institute Luxembourg for International, European and Regulatory Procedural Law	Luxemburg	mpi.lu	nicht Teil des MPG e.V. (RUFSI)
Max-Planck-Institut für Astronomie	Heidelberg	mpia.de
Max-Planck-Institut für Astrophysik	Garching	mpa-garching.mpg.de
Max-Planck-Institut für ausländisches öffentliches Recht und Völkerrecht	Heidelberg	mpil.de
Max-Planck-Institut für ausländisches und internationales Privatrecht	Hamburg	mpipriv.de
Max-Planck-Institut für ausländisches und internationales Strafrecht	Freiburg	mpicc.de
Max-Planck-Institut für Bildungsforschung	Berlin	mpib-berlin.mpg.de
Max-Planck-Institut für Biochemie	Martinsried	biochem.mpg.de
Max-Planck-Institut für Biogeochemie	Jena	bgc-jena.mpg.de
Max-Planck-Institut für Biologie des Alterns	Köln	age.mpg.de
Max-Planck-Institut für biologische Kybernetik	Tübingen	tuebingen.mpg.de
Max-Planck-Institut für Biophysik	Frankfurt am Main	mpibp-frankfurt.mpg.de
Max-Planck-Institut für Biophysik	Frankfurt am Main	biophys.mpg.de
Max-Planck-Institut für biophysikalische Chemie	Göttingen	mpibpc.mpg.de
Max-Planck-Institut für Chemie	Mainz	mpic.de
Max-Planck-Institut für chemische Energiekonversion	Mülheim an der Ruhr	cec.mpg.de
Max-Planck-Institut für chemische Ökologie	Jena	ice.mpg.de
Max-Planck-Institut für Chemische Physik fester Stoffe	Dresden	cpfs.mpg.de
Max-Planck-Institut für demografische Forschung	Rostock	demogr.mpg.de
Max-Planck-Institut für die Physik des Lichts	Erlangen	mpl.mpg.de
Max-Planck-Institut für Dynamik komplexer technischer Systeme	Magdeburg	mpi-magdeburg.mpg.de
Max-Planck-Institut für Dynamik und Selbstorganisation	Göttingen	ds.mpg.de
Max-Planck-Institut für Eisenforschung GmbH	Düsseldorf	mpie.de
Max-Planck-Institut für empirische Ästhetik	Frankfurt am Main	aesthetics.mpg.de
Max-Planck-Institut für Entwicklungsbiologie	Tübingen	tuebingen.mpg.de
Max-Planck-Institut für Entwicklungsbiologie	Tübingen	tue.mpg.de
Max-Planck-Institut für ethnologische Forschung	Halle (Saale)	eth.mpg.de
Max-Planck-Institut für europäische Rechtsgeschichte	Frankfurt/Main	mpier.uni-frankfurt.de
Max-Planck-Institut für europäische Rechtsgeschichte	Frankfurt/Main	rg.mpg.de
Max-Planck-Institut für evolutionäre Anthropologie	Leipzig	eva.mpg.de
Max-Planck-Institut für Evolutionsbiologie	Plön	evolbio.mpg.de
Max-Planck-Institut für experimentelle Medizin	Göttingen	em.mpg.de
Max-Planck-Institut für extraterrestrische Physik	Garching	mpe.mpg.de
Max-Planck-Institut für Festkörperforschung	Stuttgart	fkf.mpg.de
Max-Planck-Institut für Gesellschaftsforschung	Köln	mpifg.de
Max-Planck-Institut für Gravitationsphysik	Potsdam-Golm	aei.mpg.de
Max-Planck-Institut für Gravitationsphysik, Teilinstitut Hannover	Hannover	aei.mpg.de
Max-Planck-Institut für Herz- und Lungenforschung	Bad Nauheim	kerckhoff.mpg.de
Max-Planck-Institut für Herz- und Lungenforschung	Bad Nauheim	mpi-bn.mpg.de
Max-Planck-Institut für Hirnforschung	Frankfurt am Main	mpih-frankfurt.mpg.de
Max-Planck-Institut für Hirnforschung	Frankfurt am Main	brain.mpg.de
Max-Planck-Institut für Immunbiologie	Freiburg	immunbio.mpg.de
Max-Planck-Institut für Immunbiologie und Epigenetik	Freiburg	ie-freiburg.mpg.de
Max-Planck-Institut für Infektionsbiologie	Berlin	mpiib-berlin.mpg.de
Max-Planck-Institut für Informatik	Saarbrücken	mpi-inf.mpg.de
Max-Planck-Institut für Informatik	Saarbrücken	mpi-klsb.mpg.de
Max-Planck-Institut für Innovation und Wettbewerb	München	ip.mpg.de
Max-Planck-Institut für Intelligente Systeme, Standort Stuttgart	Stuttgart	is.mpg.de
Max-Planck-Institut für Intelligente Systeme, Standort Tübingen	Tübingen	tuebingen.mpg.de
Max-Planck-Institut für Kernphysik	Heidelberg	mpi-hd.mpg.de
Max-Planck-Institut für Kognitions- und Neurowissenschaften	Leipzig	cbs.mpg.de
Max-Planck-Institut für Kohlenforschung	Mülheim an der Ruhr	kofo.mpg.de
Max-Planck-Institut für Kolloid- und Grenzflächenforschung	Potsdam-Golm	mpikg-golm.mpg.de
Max-Planck-Institut für Kolloid- und Grenzflächenforschung	Potsdam-Golm	mpikg.mpg.de
Max-Planck-Institut für Limnologie	Plön	mpil-ploen.mpg.de	veraltet: Nachfolgeinstitut = MPI Evolutionsbiologie
Max-Planck-Institut für marine Mikrobiologie	Bremen	mpi-bremen.de
Max-Planck-Institut für Mathematik	Bonn	mpim-bonn.mpg.de
Max-Planck-Institut für Mathematik in den Naturwissenschaften	Leipzig	mis.mpg.de
Max-Planck-Institut für medizinische Forschung	Heidelberg	mpimf-heidelberg.mpg.de
Max-Planck-Institut für medizinische Forschung	Heidelberg	mr.mpg.de
Max-Planck-Institut für Menschheitsgeschichte	Jena	shh.mpg.de	Vorgängerinstitut = MPI Ökonomik
Max-Planck-Institut für Meteorologie	Hamburg	zmaw.de
Max-Planck-Institut für Meteorologie	Hamburg	mpimet.mpg.de
Max-Planck-Institut für Mikrostrukturphysik	Halle/Saale	mpi-halle.mpg.de
Max-Planck-Institut für Mikrostrukturphysik	Halle/Saale	mpi-halle.de
Max-Planck-Institut für molekulare Biomedizin	Münster	mpi-muenster.mpg.de
Max-Planck-Institut für molekulare Genetik	Berlin	molgen.mpg.de
Max-Planck-Institut für molekulare Pflanzenphysiologie	Potsdam-Golm	mpimp-golm.mpg.de
Max-Planck-Institut für molekulare Physiologie	Dortmund	cgc.mpg.de
Max-Planck-Institut für molekulare Physiologie	Dortmund	mpi-dortmund.mpg.de
Max-Planck-Institut für molekulare Zellbiologie und Genetik	Dresden	mpi-cbg.de
Max-Planck-Institut für Neurobiologie	Martinsried	neuro.mpg.de
Max-Planck-Institut für neurologische Forschung	Köln	nf.mpg.de	veraltet: Nachfolgeinstitut = MPI Stoffwechselforschung
Max-Planck-Institut für Ökonomik	Jena	econ.mpg.de	veraltet: Nachfolgeinstitut = MPI Menschheitsgeschichte
Max-Planck-Institut für Ornithologie	Seewiesen	orn.mpg.de
Max-Planck-Institut für Ornithologie, Teilinstitut Radolfzell	Radolfzell	orn.mpg.de
Max-Planck-Institut für Pflanzenzüchtungsforschung	Köln	mpipz.mpg.de
Max-Planck-Institut für Pflanzenzüchtungsforschung	Köln	mpiz-koeln.mpg.de
Max-Planck-Institut für Physik	München	mppmu.mpg.de
Max-Planck-Institut für Physik	München	mpp.mpg.de
Max-Planck-Institut für Physik komplexer Systeme	Dresden	pks.mpg.de
Max-Planck-Institut für Physik komplexer Systeme	Dresden	mpipks-dresden.mpg.de
Max-Planck-Institut für Plasmaphysik	Garching	ipp.mpg.de
Max-Planck-Institut für Plasmaphysik, Teilinstitut Greifswald	Greifswald	ipp.mpg.de
Max-Planck-Institut für Polymerforschung	Mainz	mpip-mainz.mpg.de
Max-Planck-Institut für Psychiatrie	München	mpipsykl.mpg.de
Max-Planck-Institut für Psychiatrie	München	psych.mpg.de
Max-Planck-Institut für Psycholinguistik	Nijmegen	mpi.nl
Max-Planck-Institut für Quantenoptik	Garching	mpq.mpg.de
Max-Planck-Institut für Radioastronomie	Bonn	mpifr.de
Max-Planck-Institut für Radioastronomie	Bonn	mpifr-bonn.mpg.de
Max-Planck-Institut für Softwaresysteme, Standort Kaiserslautern	Kaiserslautern	mpi-sws.org
Max-Planck-Institut für Softwaresysteme, Standort Kaiserslautern	Kaiserslautern	mpi-klsb.mpg.de
Max-Planck-Institut für Softwaresysteme, Standort Saarbrücken	Saarbrücken	mpi-klsb.mpg.de
Max-Planck-Institut für Sonnensystemforschung	Katlenburg-Lindau	mps.mpg.de
Max-Planck-Institut für Sozialrecht und Sozialpolitik	München	mpisoc.mpg.de
Max-Planck-Institut für Steuerrecht und Öffentliche Finanzen	München	tax.mpg.de
Max-Planck-Institut für Stoffwechselforschung	Köln	sf.mpg.de	Vorgängerinstitut = MPI neurologische Forschung
Max-Planck-Institut für Struktur und Dynamik der Materie	Hamburg	mpsd.mpg.de
Max-Planck-Institut für terrestrische Mikrobiologie	Marburg	mpi-marburg.mpg.de
Max-Planck-Institut für Wissenschaftsgeschichte	Berlin	mpiwg-berlin.mpg.de
Max-Planck-Institut zur Erforschung multireligiöser und multiethnischer Gesellschaften	Göttingen	mmg.mpg.de
Max-Planck-Institut zur Erforschung von Gemeinschaftsgütern	Bonn	coll.mpg.de
Max-Planck-Institut für VerhaltensbiologieKonstanzab.mpg.de	Konstanz	ab.mpg.de
Max-Planck-Forschungsstelle für die Wissenschaft der Pathogene	Berlin	mpusp.mpg.de
Mülheimer Institute	Mülheim an der Ruhr	mpi-muelheim.mpg.de	Nachfolgeinstitute: MPI chemische Energiekonversion + MPI Kohlenforschung
Stuttgarter Institute	Stuttgart	mpis.mpg.de	Nachfolgeinstitute: MPI Intelligente Systeme + MPI Festkörperforschung
'''
ACCOUNT_ACTIVATION_PATTERN = '^.*@(' + "|".join(
    map((lambda s: re.escape(s.split('\t')[2])), EMAIL_DOMAIN_LIST.splitlines())
) + ')$'
COMPILED_PATTERN = re.compile(ACCOUNT_ACTIVATION_PATTERN)

def email_in_mpg_domain_list(email):
    flag = False
    try:
        flag = re.match(COMPILED_PATTERN, email)
    except Exception as e:
        logging.error("Cannot match pattern: {}".format(e))

    return flag

def account_can_be_auto_activated(email):
    """
    account can be auto activated via activation token
    """
    # can if the uname in mpg domain
    yes_you_can =  email_in_mpg_domain_list(email)
    if not yes_you_can:
        try:
            invitations = Invitation.objects.filter(accepter=email)
            # can if at least one inviter in mpg domain
            for inv in invitations:
                if email_in_mpg_domain_list(inv.inviter):
                    return True
        except Exception as e:
            logging.error("Cannot lookup inviter: {}".format(e))

    return yes_you_can

def user_can_invite(email):
    """
    user can invite if he/she is in the mpg domain
    """
    return email_in_mpg_domain_list(email)

if __name__ == "__main__":
    print(ACCOUNT_ACTIVATION_PATTERN)
    # if account_can_be_auto_activated('some_user@mpdl.mpg.de'):
    if not account_can_be_auto_activated('test_email_for_non_mpg_domain@gmail.com'):
        print('NOT ', end='')
    print('Matched')

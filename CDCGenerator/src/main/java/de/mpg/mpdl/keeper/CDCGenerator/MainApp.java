package de.mpg.mpdl.keeper.CDCGenerator;

import net.sf.jasperreports.engine.JREmptyDataSource;
import net.sf.jasperreports.engine.JasperExportManager;
import net.sf.jasperreports.engine.JasperFillManager;
import net.sf.jasperreports.engine.JasperPrint;
import net.sf.jasperreports.engine.JasperReport;
import net.sf.jasperreports.engine.util.JRLoader;
import net.sf.jasperreports.engine.util.JRSaver;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

import static net.sf.jasperreports.engine.JasperCompileManager.compileReport;

public class MainApp {
/*
    Call from the command line should look like:
    $ java -cp "CDCGenerator.jar:fonts-ext.jar" de.mpg.mpdl.keeper.CDCGenerator.MainApp -i 1 -aa "Author1, Author2" -d "Description" -c "keeper@mpdl.mpg.de" -u "http://keeper.mpdl.mpg.de/library" -t "Project 1" CDC.pdf
    java -jar CDCGenerator.jar does not work due to bad resolution of font extensions in JasperReports
*/

    public static final String DEFAULT_CDC_JRXML = "CDC.jrxml";
    private static final String DEFAULT_CDC_JASPER =  "CDC.jasper";
    private static final String DEFAULT_CDC_PDF = "CDC.pdf";

    private static Options options = new Options();

    //CLI options
    private enum OPTS {
        ID("i", "id", "Certificate ID", true),
        TITLE("t", "title", "Title of Project/Library", true),
        AUTHORS_AND_AFFILIATIONS("aa", "authors_and_affiliations", "Authors and Affiliations", true),
        DESCRIPTION("d", "description", "Project/Library Description", true),
        CONTACT("c", "contact", "Contact email", true),
        URL("u", "url", "Link to the Project/Library location", true),
        GENERATE_JR("g", "generate-jr", "Generate JasperReport from JRXML", false),
        HELP("h", "help", "Help", false);

        private final String opt;
        private final String longOpt;
        private final String description;
        private final boolean hasArgs;

        OPTS(String opt, String longOpt, String description, boolean hasArgs) {
            this.opt = opt;
            this.longOpt = longOpt;
            this.description = description;
            this.hasArgs = hasArgs;
        }

        public String getOpt() {
            return opt;
        }

        public String getLongOpt() {
            return longOpt;
        }

        public String getDescription() {
            return description;
        }

        public boolean hasArgs() {
            return hasArgs;
        }
    }

    public static void main(String[] args) {


        //init OPTS
        for (OPTS p: OPTS.values())
            options.addOption(Option.builder(p.getOpt())
                    .longOpt(p.getLongOpt())
                    .hasArg(p.hasArgs)
                    .desc(p.getDescription())
                    .required(p != OPTS.HELP && p != OPTS.GENERATE_JR)
                    .build());

        //parse command line
        CommandLineParser parser = new DefaultParser();

        CommandLine cl = null;
        Map<String, Object> parameters = new HashMap<>();
        try {
            cl = parser.parse(options, args);
            for (OPTS p: OPTS.values()) {
                if (p.hasArgs()) {
                    parameters.put(p.name(), cl.getOptionValue(p.getOpt()));
                }
            }


            if (cl.hasOption(OPTS.HELP.getOpt()))
                help();

            if (cl.getOptions().length == 0) {
                System.out.println();
                help();
            }


        } catch (ParseException e) {
            e.printStackTrace();
            help();
        }

        try {
            JasperReport jasperReport;

            if (cl.hasOption(OPTS.GENERATE_JR.getOpt())) {
                jasperReport = compileReport(MainApp.class.getResourceAsStream("/" + DEFAULT_CDC_JRXML));
                JRSaver.saveObject(jasperReport, "src/main/resources/" + DEFAULT_CDC_JASPER);
            } else {
                jasperReport = (JasperReport) JRLoader.loadObject(MainApp.class.getResourceAsStream("/" + DEFAULT_CDC_JASPER));
            }



            JasperPrint jasperPrint = JasperFillManager.fillReport(
                    jasperReport,
                    parameters,
                    new JREmptyDataSource()
            );

            String CDC_PDF = cl.getArgs().length > 0 ? cl.getArgs()[0] : DEFAULT_CDC_PDF;

            JasperExportManager.exportReportToPdfFile(jasperPrint, CDC_PDF);
//            JasperViewer jasperViewer = new JasperViewer(jasperPrint);
//            jasperViewer.setVisible(true);

            File cdc = new File(CDC_PDF);
            if (cdc.exists()) {
                System.out.println( "CDC successfully generated: " + CDC_PDF + " (" + (cdc.length() / 1024)  + "Kb)");
            } else {
                System.exit(1);
            }


        } catch (Exception ex) {
            System.out.println( "Unexpected exception:" + ex.getMessage() );
        }

    }

    private static void help() {
       HelpFormatter formatter = new HelpFormatter();
       formatter.printHelp("class opt1 val1, opt2 val2,... [output pdf]", options);
    }
}

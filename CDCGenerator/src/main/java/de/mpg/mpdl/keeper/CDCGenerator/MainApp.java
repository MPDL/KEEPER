package de.mpg.mpdl.keeper.CDCGenerator;

import net.sf.jasperreports.engine.JREmptyDataSource;
import net.sf.jasperreports.engine.JRException;
import net.sf.jasperreports.engine.JasperExportManager;
import net.sf.jasperreports.engine.JasperFillManager;
import net.sf.jasperreports.engine.JasperPrint;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import java.util.HashMap;
import java.util.Map;

import static net.sf.jasperreports.engine.JasperCompileManager.compileReport;

public class MainApp {

    public static final String DEFAULT_CDC_JRXML = "src/main/resources/CDC.jrxml";

    private static Options options = new Options();

    //CLI options
    private enum OPTS {
        ID("i", "id", "Certificate ID", true),
        TITLE("t", "title", "Title of Project/Library", true),
        AUTHORS_AND_AFFILIATIONS("aa", "authors_and_affiliations", "Authors and Affiliations", true),
        DESCRIPTION("d", "description", "Project/Library Description", true),
        CONTACT("c", "contact", "Contact email", true),
        URL("u", "url", "Link to the Project/Library location", true),
        OUTPUT("o", "output", "Path to generated Certificate", true),
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
        for (OPTS p: OPTS.values()) {
            options.addOption(p.getOpt(), p.getLongOpt(), p.hasArgs, p.getDescription());
        }

        //parse command line
        CommandLineParser parser = new DefaultParser();

        //populate JasperReport parameters
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

        } catch (ParseException e) {
            System.out.println( "Unexpected exception:" + e.getMessage() );
            help();
        }

        try {
            JasperPrint jasperPrint = JasperFillManager.fillReport(
                    compileReport(DEFAULT_CDC_JRXML),
                    parameters,
                    new JREmptyDataSource()
            );

            JasperExportManager.exportReportToPdfFile(jasperPrint, cl.getOptionValue(OPTS.OUTPUT.getOpt()));
//            JasperViewer jasperViewer = new JasperViewer(jasperPrint);
//            jasperViewer.setVisible(true);
        } catch (JRException ex) {
            System.out.println( "Unexpected exception:" + ex.getMessage() );
        }

    }

    private static void help() {
       HelpFormatter formatter = new HelpFormatter();
       formatter.printHelp("Main", options);
        //System.exit(0);
    }
}

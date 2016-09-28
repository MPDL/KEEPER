import de.mpg.mpdl.keeper.CDCGenerator.MainApp;

import org.junit.Ignore;
import org.junit.Test;

import java.io.File;

import static org.junit.Assert.assertTrue;

/**
 * Created by vlad on 08.07.16.
 */
public class TestCDCGenerator {

    public static final String PATH_TO_CDC_PDF = "target/CDC.pdf";
    public static final String PATH_TO_CDC_LONG_META_PDF = "target/CDC_long_meta.pdf";

    @Ignore
    @Test
    public void testCDCGenerator() throws Exception {
        MainApp.main(new String[]{
                "-i", "1",
                "-aa", "\"Author1, Author2, Author3\"",
                "-c", "keeper@mpdl.mpg.de",
                "-d", "\"Description of the archived project\"",
                "-t", "\"Library Title\"",
                "-u", "\"https://keeper.mpdl.mpg.de/mylibrary\"",
                "-g",
                "-h",
                PATH_TO_CDC_PDF
//                "Argument2"
        });
        File f = new File(PATH_TO_CDC_PDF);
        assertTrue("Cannot find generated pdf at " + f.getAbsolutePath(), f.exists());

    }

//    @Ignore
    @Test
    public void testCDCGenerator_Long_Meta() throws Exception {
        MainApp.main(new String[]{
                "-i", "1",
                "-aa", "\"Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2\"",
                "-c", "keeper@mpdl.mpg.de",
                "-d", "\"Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project  Description of the archived project Description of the archived project Description of the archived project  Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project\"",
                "-t", "\"Very Long Title Longer As Wwo Lines Should be Cut Maximal Two Lines Plus Very Long Title Longer As Wwo Lines Should be Cut Maximal Two Lines Plus Very Long Title Longer As Wwo Lines Should be Cut Maximal Two Lines Plus Very Long Title Longer As Wwo Lines Should be Cut Maximal Two Lines Plus Very Long Title Longer As Wwowwwwwwwwwwwwwww Lines Should be Cut Maximal Two Lines Plus ...\"",
                "-u", "\"https://keeper.mpdl.mpg.de/mylibrary\"",
                "-g",
                "-h",
                PATH_TO_CDC_LONG_META_PDF
//                "Argument2"
        });
        File f = new File(PATH_TO_CDC_PDF);
        assertTrue("Cannot find generated pdf at " + f.getAbsolutePath(), f.exists());

    }



}

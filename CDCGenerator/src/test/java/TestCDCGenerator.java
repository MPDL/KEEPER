import de.mpg.mpdl.keeper.CDCGenerator.MainApp;

import org.junit.Ignore;
import org.junit.Test;

import java.io.File;

import static org.junit.Assert.assertTrue;

/**
 * Created by vlad on 08.07.16.
 */
public class TestCDCGenerator {


    //@Ignore
    @Test
    public void testCDCGenerator() throws Exception {
        String fn = "target/CDC.pdf";
        MainApp.main(new String[]{
                "-i", "1",
                "-aa", "\"Author1, Author2, Author3\"",
                "-c", "keeper@mpdl.mpg.de",
                "-d", "\"Hallo !!! 倗冡厤!!! Привет!!! Description of the archived project&quote;In apos!!!&quote;\"",
                "-t", "\"\"Library Title 2 &quote;In apos!!!&quote;\"",
                "-u", "\"https://keeper.mpdl.mpg.de/mylibrary\"",
                "-g",
                "-h",
                fn
//                "Argument2"
        });
        File f = new File(fn);
        assertTrue("Cannot find generated pdf at " + f.getAbsolutePath(), f.exists());

    }

    @Ignore
    @Test
    public void testCDCGenerator_Long_Meta() throws Exception {
        String fn = "target/CDC_long_meta.pdf";
        MainApp.main(new String[]{
                "-i", "1",
                "-aa", "\"Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2, Author1, Author2\"",
                "-c", "keeper@mpdl.mpg.de",
                "-d", "\"Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project  Description of the archived project Description of the archived project Description of the archived project  Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project Description of the archived project\"",
                "-t", "\"Very Long Title Longer As Wwo Lines Should be Cut Maximal Two Lines Plus Very Long Title Longer As Wwo Lines Should be Cut Maximal Two Lines Plus Very Long Title Longer As Wwo Lines Should be Cut Maximal Two Lines Plus Very Long Title Longer As Wwo Lines Should be Cut Maximal Two Lines Plus Very Long Title Longer As Wwowwwwwwwwwwwwwww Lines Should be Cut Maximal Two Lines Plus ...\"",
                "-u", "\"https://keeper.mpdl.mpg.de/mylibrary\"",
                "-g",
                "-h",
                fn
//                "Argument2"
        });
        File f = new File(fn);
        assertTrue("Cannot find generated pdf at " + f.getAbsolutePath(), f.exists());

    }



}

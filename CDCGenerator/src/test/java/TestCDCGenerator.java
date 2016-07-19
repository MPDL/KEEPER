import de.mpg.mpdl.keeper.CDCGenerator.MainApp;

import org.junit.Test;

import java.io.File;

import static org.junit.Assert.assertTrue;

/**
 * Created by vlad on 08.07.16.
 */
public class TestCDCGenerator {

    public static final String PATH_TO_CDC_PDF = "src/main/resources/CDC.pdf";

    @Test
    public void testCDCGenerator() throws Exception {
        MainApp.main(new String[]{
                "-i", "1",
                "-aa", "\"Vlad Makarenko\"",
                "-c", "\"makarenko@mpdl.mpg.de",
                "-d", "\"The very first archived Project\"",
                "-t", "\"Library Title\"",
                "-u", "\"https://keeper.mpdl.mpg.de/mylibrary\"",
                "-o", PATH_TO_CDC_PDF,
                "-h"
        });
        File f = new File(PATH_TO_CDC_PDF);
        assertTrue("Cannot find generated pdf at " + f.getAbsolutePath(), f.exists());

    }

}

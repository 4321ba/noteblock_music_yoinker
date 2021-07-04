package ab.noteblock_music_yoinker;

import net.minecraftforge.fml.common.Mod;

import net.minecraft.client.settings.KeyBinding;
import net.minecraftforge.fml.client.registry.ClientRegistry;
import org.lwjgl.input.Keyboard;

import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;

import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.gameevent.InputEvent.KeyInputEvent;
import net.minecraftforge.client.event.sound.PlaySoundSourceEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent.ClientTickEvent;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@Mod(modid = "noteblock_music_yoinker", clientSideOnly = true, name = "Noteblock Music Yoinker", version = "1.1")
@Mod.EventBusSubscriber
public class NoteblockMusicYoinker
{
    // directly reference a log4j logger.
    private static final Logger LOGGER = LogManager.getLogger();
    
    private static KeyBinding recordBinding = new KeyBinding("key.record.desc", Keyboard.KEY_R, "key.noteblock_music_yoinker.category");

    private static int time_passed = 0;
    private static boolean is_writing_to_file = false;
    private static String file_to_write;

    @EventHandler
    public static void init(FMLInitializationEvent event) {
        ClientRegistry.registerKeyBinding(recordBinding);
    }

    @SubscribeEvent
    public static void onClientTick(ClientTickEvent event) {
        if (is_writing_to_file) ++time_passed;
    }

    @SubscribeEvent
    public static void onKeyPress(KeyInputEvent event) {
        // filter for the registered key binding
        if (!recordBinding.isPressed()) return;
        is_writing_to_file = !is_writing_to_file;
        if (is_writing_to_file) {
            file_to_write = "recorded_music/" + java.time.LocalDateTime.now().format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss")) + ".csv";
            // make a folder if there isn't one
            File theDir = new File("recorded_music");
            if (!theDir.exists()) theDir.mkdirs();
            LOGGER.info("Started recording to file " + file_to_write + ".");
        } else {
            time_passed = 0;
            LOGGER.info("Stopped recording to file " + file_to_write + ".");
        }
    }

    @SubscribeEvent
    public static void onSoundPlayed(PlaySoundSourceEvent event) {
        String sound_category = event.getSound().getCategory().getName();
        //LOGGER.info("Sound played with category " + sound_category + ".");
        // test if the sound is of record category and if we're recording
        if (!sound_category.equals("record") || !is_writing_to_file) return;
        String[] split_up_name = event.getName().split("[.]");
        //we don't want to have "block.note.harp", only "harp" for backwards compatibility and easier readability
        //but we need the whole "entity.silverfish.hurt" e.g. for the other, non-noteblock sounds, that are part of the piece
        String name = (split_up_name[0].equals("block") && split_up_name[1].equals("note")) ? split_up_name[2] : event.getName();
        float pitch = event.getSound().getPitch();
        float volume = event.getSound().getVolume();
        //LOGGER.info("Recording " + name + " at time " + time_passed + " with pitch " + pitch + " and volume " + volume + ".");
        try {
            // we're opening and closing the file every time we add a line to it, performance could be improved maybe
            FileWriter myWriter = new FileWriter(file_to_write, true);
            myWriter.append(name + "," + time_passed + "," + pitch + "," + volume + "\n");
            myWriter.close();
        } catch (IOException e) {
            LOGGER.error("Error writing to file " + file_to_write + ".");
            e.printStackTrace();
        }
        time_passed = 0;
    }

}

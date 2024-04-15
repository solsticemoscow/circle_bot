import asyncio
from typing import Union
from PIL import Image

from moviepy.editor import *
from moviepy.video.fx.crop import crop
from moviepy.video.fx.loop import loop
from pydub import AudioSegment
from moviepy.config import change_settings

from BOT.config import DATA_INPUT, ROOT_DIR, THREADS



class VideoNote:
    video: Union[VideoClip, None]
    audio: Union[AudioFileClip, None]
    telegram_id: int
    video_note_time: int

    def __init__(self, telegram_id, video_note_time, repeats=5):
        if not os.path.exists(f"{DATA_INPUT}{telegram_id}"):
            os.makedirs(f"{DATA_INPUT}{telegram_id}")

        if os.path.exists(f'{DATA_INPUT}{telegram_id}/video.mp4'):
            video = (VideoFileClip(f'{DATA_INPUT}{telegram_id}/video.mp4'))
        else:
            if "image.jpg" in os.listdir(f"{DATA_INPUT}{telegram_id}/"):
                clips = ImageClip(f"{DATA_INPUT}{telegram_id}/image.jpg").set_duration(video_note_time)
                self.video_note_time = video_note_time
            else:
                clips = VideoFileClip(f"{DATA_INPUT}{telegram_id}/animation.gif")
                clips = loop(clips, n=repeats)

                self.video_note_time = clips.duration
            video = clips

        audio = None
        if os.path.exists(f'{DATA_INPUT}{telegram_id}/music.mp3'):
            raw_audio = AudioSegment.from_file(f'{DATA_INPUT}{telegram_id}/music.mp3')
            raw_audio_len = raw_audio.duration_seconds
            silence = AudioSegment.silent(max(0, (10 - raw_audio_len) * 1000))
            combined_audio = raw_audio + silence
            combined_audio.export(f'{DATA_INPUT}{telegram_id}/audio_proc.mp3', format='mp3')

            audio = AudioFileClip(f'{DATA_INPUT}{telegram_id}/audio_proc.mp3')
        video = video.set_duration(video.duration)
        self.video = video
        self.audio = audio
        self.telegram_id = telegram_id
        self.video_note_time = video.duration

        self.texture = None
        for i in os.listdir(f"{DATA_INPUT}{telegram_id}"):
            if "texture" in i:
                self.texture = ImageClip(f'{DATA_INPUT}{telegram_id}/texture.png').set_duration(self.video.duration).resize(width=640)


    async def compose(self):
        png_path = DATA_INPUT + str(self.telegram_id) + '/texture.png'
        png_image = Image.open(png_path).convert("RGBA")

        jpg_path = DATA_INPUT + str(self.telegram_id) + '/image_for_texture.jpg'
        jpg_image = Image.open(jpg_path)
        jpg_image = jpg_image.resize(png_image.size)

        for x in range(min(jpg_image.width, png_image.width)):
            for y in range(min(jpg_image.height, png_image.height)):
                r, g, b, a = png_image.getpixel((x, y))
                if a != 0:
                    jpg_pixel = jpg_image.getpixel((x, y))
                    png_image.putpixel((x, y), jpg_pixel)


        result_path = DATA_INPUT + str(self.telegram_id) + '/composed.png'
        png_image.save(result_path, "PNG")
        self.texture = ImageClip(result_path).set_duration(self.video.duration).resize(width=640)


    async def add_audio(self):
        audio = self.audio
        video_note = self.video.set_audio(audio)
        video_note = video_note.set_duration(self.video_note_time)
        self.video = video_note


    async def crop(self):
        original_clip = self.video
        (w, h) = original_clip.size

        if w > h:
            crop_clip = crop(original_clip, width=h, height=h, x_center=w / 2, y_center=h / 2)
        else:
            crop_clip = crop(original_clip, width=w, height=w, x_center=w / 2, y_center=h / 2)
        final_clip = crop_clip.resize(width=640)

        self.video = final_clip


    async def add_effect(self, effect: ImageClip):
        change_settings({"IMAGEMAGICK_BINARY": r"/usr/bin/convert"})
        result = CompositeVideoClip([self.video, effect])
        result.duration = self.video.duration
        self.video = result

    async def add_texture(self):
        await VideoNote.add_effect(self, self.texture)

    async def add_watermark(self):
        watermark = ImageClip(img=ROOT_DIR + '/data/video_round_bot.png').set_duration(self.video.duration).resize(width=640)
        await VideoNote.add_effect(self, watermark)

    async def write_to_disk(self):
        try:
            name: str = f'{DATA_INPUT}{self.telegram_id}/video_final.mp4'
            self.video = self.video.set_duration(min(self.video.duration, 59))

            bitrate = (8 * (10 * 1024)) / self.video.duration - 256 - 2

            self.video.write_videofile(name,
                                       threads=THREADS,
                                       preset="medium",
                                       fps=30,
                                       bitrate=f"{bitrate}k",
                                       audio_bitrate="256k",
                                       codec="libx264",
                                       ffmpeg_params=["-tune", "film"]
                                       )
            return 'Задача успешно завершилась!'
        except Exception as e:
            return e


import logging

import cv2
import keyboard
import mediapipe as mp
import nest_asyncio
import numpy as np
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram import __version__ as TG_VER
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
        np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle


def curl(counter, stage, landmarks, image):
    # Get coordinates
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
             landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
             landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

    # Calculate angle
    angle = calculate_angle(shoulder, elbow, wrist)

    # Visualize angle
    cv2.putText(image, str(angle),
                tuple(np.multiply(elbow, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                )

    # Curl counter logic
    if angle > 160:
        stage = "down"
    if angle < 30 and stage == 'down':
        stage = "up"
        counter += 1
        print(counter)
    return counter, stage


def lateral(counter, stage, landmarks, image):
    # Get coordinates
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
             landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
             landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]

    # Calculate angle
    angle_elbow = calculate_angle(shoulder, elbow, wrist)
    angle_shoulder = calculate_angle(hip, shoulder, elbow)

    # Visualize angle
    cv2.putText(image, str(angle_elbow),
                tuple(np.multiply(elbow, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2,
                cv2.LINE_AA)
    cv2.putText(image, str(angle_shoulder),
                tuple(np.multiply(shoulder, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2,
                cv2.LINE_AA)
    # Lateral raise counter logic
    if angle_elbow > 160 and angle_elbow < 180:
        if angle_shoulder > 90:
            stage = "down"
        if angle_shoulder < 30 and stage == 'down':
            stage = "up"
            counter += 1
            print(counter)
    return counter, stage


def squat(counter, stage, landmarks, image):
    # Get coordinates
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    heel = [landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]

    # Calculate angle
    angle_knee = calculate_angle(hip, knee, ankle)
    angle_ankle = calculate_angle(knee, ankle, heel)

    # Visualize angle
    cv2.putText(image, str(angle_knee),
                tuple(np.multiply(knee, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,
                                                255, 255), 2, cv2.LINE_AA
                )
    cv2.putText(image, str(angle_ankle),
                tuple(np.multiply(ankle, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,
                                                255, 255), 2, cv2.LINE_AA
                )
    # Squats raise counter logic
    if angle_knee > 170:
        stage = "up"
    if angle_knee < 90 and stage == 'up':
        stage = "down"
        counter += 1
        print(counter)
    return counter, stage


def exerciser(options, choice):
    global cam_run
    global cap
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cam_run = True

    # Curl counter variables
    counter = 0
    stage = None

    # Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()

            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                counter, stage = options[choice](
                    counter, stage, landmarks, image)

            except:
                pass

            # Render curl counter
            # Setup status box
            cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

            # Rep data
            cv2.putText(image, 'REPS', (15, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Stage data
            cv2.putText(image, 'STAGE', (65, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, stage,
                        (60, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

            cv2.imshow('Mediapipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    return counter


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
bot_token = "5885078983:AAF2_Pmh_FS3gDHdm98bcyj6NYgy0Jr97ac"
nest_asyncio.apply()


#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""


try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GENDER, BIO, BICEP_CURL, LATERAL_RAISE, SQUAT = range(5)
exercises = {
    "bicep curl": curl,
    "lateral raise": lateral,
    "squats": squat,
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Boy", "Girl", "Other"]]
    await update.message.reply_text(
        "Hi! My name is Professor Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
        ),
    )

    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "I see! tell me something about yourself, "
        "so I know something about you, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return BIO

'''async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return LOCATION'''


'''async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "I bet you look great! Now, send me your location please, or send /skip."
    )

    return LOCATION'''


'''async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        "Maybe I can visit you sometime! At last, tell me something about yourself."
    )

    return BIO'''


'''async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "You seem a bit paranoid! At last, tell me something about yourself."
    )

    return BIO'''


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Thank you! reply with the following commands to get started: \n1.Bicep Curl \n2.Lateral Raise \n3.Squat \n /cancel to end the conversation")


async def skip_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the bio and asks for exercise."""
    user = update.message.from_user
    logger.info("User %s did not send a bio", user.first_name)
    await update.message.reply_text(
        "Reply with the following commands to get started: \n1. /Bicep_Curl \n2. /Lateral_Raise \n3. /Squat \n /cancel to end the conversation"
    )
    print("user here")


async def Bicep_Curl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("bicep curl")
    global cam_run
    cam_run = True
    user = update.message.from_user
    logger.info("User %s chose Bicep Curl", user.first_name)
    await update.message.reply_text(
        "Starting Bicep curls!\nReply with the following commands to continue: \n /end to go back to exercise menu \n /cancel to end the conversation"
    )
    counter = exerciser(exercises, "bicep curl", cam_run)
    await update.message.reply_text(
        f"Done with Bicep curls! reps done {counter}"
    )


async def Lateral_Raise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global cam_run
    cam_run = True
    user = update.message.from_user
    logger.info("User %s chose Lateral Raise", user.first_name)
    await update.message.reply_text(
        "Starting Lateral Raises!\nReply with the following commands to continue: \n /end to go back to exercise menu \n /cancel to end the conversation"
    )
    counter = exerciser(exercises, "lateral raise", cam_run)
    await update.message.reply_text(
        f"Done with Lateral Raises! reps done {counter}"
    )


async def Squat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global cam_run
    cam_run = True
    user = update.message.from_user
    logger.info("User %s chose Squat", user.first_name)
    await update.message.reply_text(
        "Starting Squats!\nReply with the following commands to continue: \n /end to go back to exercise menu \n /cancel to end the conversation"
    )
    counter = exerciser(exercises, "squat", cam_run)
    await update.message.reply_text(
        f"Done with Squats! reps done {counter}"
    )


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global cam_run
    if cam_run == True:
        user = update.message.from_user
        logger.info("%s ended the exercise", user.first_name)
        cap.release()
        cam_run = False
        await update.message.reply_text("Thank you! reply with the following commands to get started again: \n1. /Bicep_Curl \n2. /Lateral_Raise \n3. /Squat \n /cancel to end the conversation")
        if(text not in exercises.keys()):
            await update.message.reply_text("Sorry, I don't know that exercise. Please try again.")
            return ConversationHandler.END
    else:
        await update.message.reply_text("You are not doing an exercise right now. Please try again.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # Add conversation handler with the states GENDER, BIO and EXERCISE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio), CommandHandler("skip", skip_bio), CommandHandler("Bicep_Curl", Bicep_Curl), CommandHandler("Lateral_Raise", Lateral_Raise), CommandHandler("Squat", Squat)],
            BICEP_CURL: [MessageHandler(filters.TEXT & ~filters.COMMAND, Bicep_Curl), CommandHandler("end", end)],
            LATERAL_RAISE: [MessageHandler(filters.TEXT & ~filters.COMMAND, Lateral_Raise), CommandHandler("end", end)],
            SQUAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, Squat), CommandHandler("end", end)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

import { phone_icon_green, drone_icon_green, coords, history_icon, satellite_icon_green, grid_icon, lidar_icon, tree_icon } from "../assets/icons";
import { good_example, bad_example_busy, bad_example_size, toggle_partial, toggle_genus, resolution_estimation, long_lat, good_image_drone_rgb, bad_image_drone_rgb } from "../assets/images";

export const backendURL = "http://127.0.0.1:8000";

export const helpLinks = [
  {
    label: 'Phone Classification',
    link: '/help/ground'
  },
  {
    label: 'Drone RGB Classification',
    link: '/help/droneRGB'
  },
  {
    label: 'Satellite Classification',
    link: '/help/satellite'
  },
  {
    label: 'Drone RGB Segmentation',
    link: '/help/droneSegmentation'
  },
]

export const help = [
  {
    title: "Help for Image Upload Classification",
    body: 'Let us teach you how to take better drone images and improve the results our app can produce for you. We can also explain to you what the options on for drone RGB classification do and walk you through how to get started classifying your own images!',
    link: '/help/droneRGB',
    icon: drone_icon_green,
  },
  {
    title: 'Help for Coordinates Input Classification',
    body: 'Let us explain to you what the options on for Satellite classification do and walk you through how to get started classifying any area of your choosing!',
    link: '/help/satellite',
    icon: coords,
  },
]


export const helpDroneRGB = [
  {
    title: 'Steps To Upload And Classify Drone RGB Images',
    sections: [
      {
        title: 'Step 1: Click "Select File" and choose an image',
        body: 'Once you click "Select File", you will see the options to upload a file from your device. If you are on a phone, you may also see the option to take a picture. After selecting an image or taking a picture, a preview of your image should be visible to let you know it is uploaded. For tips on how to get good images, refer to the section below.',
      },
      {
        title: 'Step 2: Set The Species Genus Toggle',
        body: "Next, choose whether you want your image to be classified by species or genus.",
      },
      {
        title: 'Step 3: Enter a Resolution Estimation',
        body: "Next, enter a resolution estimation for your uploaded image. This estimation should have the units of cm/pixel. For more information on what this means, refer to the section on how to get good images.",
      },
      {
        title: 'Step 4: Click "Classify Image" and View Your Results',
        body: 'Once you have uploaded your image, set your toggle, and entered a resolution estimation, then click click "Classify Image". After a short loading process, the results from the classification will be available. You can check the classification of individual areas in the image and you can also see the probabilities of the species of genuses in our circular chart.',
      },
    ]
  },
  {
    title: 'How To Take Good Pictures',
    sections: [
      {
        title: 'What Do Good Pictures Look Like?',
        body: "For drone classification, our app uses canopy-level aerial images to predict the species or genus of the area. To ensure accurate classification, the images you upload should be taken directly over the tree area, clearly capturing the canopy and surrounding features. Ideally, images should be captured from a distance of approximately 50 m to 60 m, with no zoom applied and minimal motion blur or distortion.",
        image: good_image_drone_rgb,
      },
      {
        title: 'Image Quality',
        body: "It is recommended to upload images with a resolution similar to the training data, which was captured at approximately 15–20 cm per pixel. All uploaded images will be resized to match the spatial scale used during training to preserve pattern consistency. Very low-resolution images may result in reduced prediction accuracy due to the loss of fine-grained canopy details.",
      },
    ]
  },
  {
    title: 'Bad Pictures and What To Avoid',
    sections: [
      {
        body: "A bad picture can seriously affect the quality of the results our app can produce. Below we will try to point out a few thing to avoid.",
      },
      {
        title: 'Wrong Perspective',
        body: "To ensure accurate predictions, avoid uploading images taken from angles other than a top-down canopy view. Side views or angled shots will definitly lead to incorrect classification.",
        image: bad_image_drone_rgb,
      },
      {
        title: 'Images With High Resolution',
        body: "Another thing to avoid when uploading images is using extremely high-resolution files. While clarity is important, high-resolution images do not match the resolution the model was trained on. Aim for images around 15~20 cm pixel resolution for best results.",
      },
    ]
  },
  {
    title: 'Drone RGB Options and What They Do',
    sections: [
      {
        title: 'Species and Genus Toggle',
        body: "The species and genus toggle is used so that the user can choose the level of classification. When the toggle is to the left, the tree will be classified by species. When the toggle is to the right, the uploaded image will be classified by genus.",
        image: toggle_genus,
      },
      {
        title: 'Resolution Estimation',
        body: "The resolution estimation is needed to help understand how much ground area is represented by the width and height of your uploaded image. This is then used to break your image into appropriately sized sections that can be classified by out app into their respective species or genus.",
        image: resolution_estimation,
      },
    ]
  }
]

export const helpCoordinates = [
  {
    title: 'Steps To Upload And Classify Drone RGB Images',
    sections: [
      {
        title: 'Step 1: Set The Species Genus Toggle',
        body: "Next, choose whether you want your image to be classified by species or genus.",
      },
      {
        title: 'Step 2: Enter a Longitude and Latitude',
        body: "Next, enter a the longitude and latitude of the area you want to be classified. Remember, this location will be centered in the classified image.",
      },
      {
        title: 'Step 3: Click "Classify Image" and View Your Results',
        body: 'Once you have set your toggle and entered a longitude and latitude, then click click "Classify Image". After a short loading process, the results from the classification will be available. You can check the classification of individual areas in the image and you can also see the probabilities of the species of genuses in our circular chart.',
      },
    ]
  },
  {
    title: 'Drone RGB Options and What They Do',
    sections: [
      {
        title: 'Species and Genus Toggle',
        body: "The species and genus toggle is used so that the user can choose the level of classification. When the toggle is to the left, the tree will be classified by species. When the toggle is to the right, the uploaded image will be classified by genus.",
        image: toggle_genus,
      },
      {
        title: 'Latitude and Longitude',
        body: "Enter both the longitude and latitude of the area you want to be classified. The coordinates you enter will be centered in the image that get classified. Also, make sure to enter the longitude and latitude in the decimal degrees form since the input only allows positive and negative numbers. An example of this form is: 49.259389, -123.224408.",
        image: long_lat,
      },
    ]
  }
]

export const helpDroneSeg = [
  {
    title: 'Steps To Upload And Segment Drone RGB Images',
    sections: [
      {
        title: 'Step 1: Click "Select File" and choose an image',
        body: 'Once you click "Select File", you will see the options to upload a file from your device.',
      },
      {
        title: 'Step 2: Enter a Resolution Estimation',
        body: "Next, enter a resolution (ground sampling distance) estimation for your uploaded image. This estimation should have the units of cm/pixel.As a reference the gsd for training images are in a range of 1.81 to 2.02 cm. ",
      },
      {
        title: 'Step 3: Click "Segment Image" and View Your Results',
        body: 'Once you have uploaded your image, set your toggle, and entered a resolution estimation, then click click "Segment Image". After a short loading process, the results from the segmentation will be available, with the mask overlap with the original image, there is option to turn the overlap on and off. There is also a download option for you to download the files. On the right will show the percentage of each genus that are identified in the image',
      },
    ]
  },
]
export const mainUploadLinks = [
  {
    label: 'Image Upload',
    link: '/upload/drone/RGB',
    icon: drone_icon_green
  },
  {
    label: 'Coordinates Input',
    link: '/upload/satellite',
    icon: satellite_icon_green
  },
]

export const dashboardLinks = [
  {
    label: 'View History',
    link: '/accounts/history',
    icon: history_icon
  }
]

export const droneOptions = [

  {
    label: 'GRID CLASSIFICATION',
    link: '/upload/drone/RGB',
    icon: grid_icon
  },
]

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
    title: 'Help for Phone Classification',
    body: 'Let us teach you how to take better pictures and improve the results our app can produce for you. We can also explain to you what the options on for phone classification do and walk you through how to get started classifying your own pictures!',
    link: '/help/ground',
    icon: phone_icon_green,
  },
  {
    title: "Help for Drone RGB Classification",
    body: 'Let us teach you how to take better drone images and improve the results our app can produce for you. We can also explain to you what the options on for drone RGB classification do and walk you through how to get started classifying your own images!',
    link: '/help/droneRGB',
    icon: drone_icon_green,
  },
  {
    title: 'Help for Satellite Classification',
    body: 'Let us explain to you what the options on for Satellite classification do and walk you through how to get started classifying any area of your choosing!',
    link: '/help/satellite',
    icon: coords,
  },
  {
    title: 'Help for Drone RGB Segmentation',
    body: 'Let us explain to you what the drone segmentation does and walk you through how to get started segmenting any drone RGB image!',
    link: '/help/droneSegmentation',
    //icon: , #not sure what icons to use
  }
]

export const helpGround = [
  {
    title: 'Steps To Upload And Classify Phone Images',
    sections: [
      {
        title: 'Step 1: Click "Select File" and choose an image',
        body: 'Once you click "Select File", you will see the options to upload a file from your device. If you are on a phone, you may also see the option to take a picture. After selecting an image or taking a picture, a preview of your image should be visible to let you know it is uploaded. For tips on how to take good photos, refer to the section below.',
      },
      {
        title: 'Step 2: Set your Toggles',
        body: "Next, set your toggles. Choose whether you want your image to be classified by species or genus, and against our full library of species or genus, or just the subset to obtain better results.",
      },
      {
        title: 'Step 3: Click "Classify Image" and View Your Results',
        body: 'Once you have uploaded your image and set your toggles, click "Classify Image". After a short loading process, the results from the classification will be available. You can check that the tree was properly detected in the image and you can also see the probabilities of the species of genuses in our circular chart.',
      },
    ]
  },
  {
    title: 'How To Take Good Pictures',
    sections: [
      {
        title: 'What Do Good Pictures Look Like?',
        body: "For phone classification, our app uses the the tree bark to predict the species or genus of the tree. This means that in order an accurate classification, the images you upload should have a tree trunk in clear view. The ideal image is taken between roughly 20cm and 60cm away, without any zoom or blurriness.",
        image: good_example,
      },
      {
        title: 'Image Contents and Cropping',
        body: "The image above shows an example of what a good image looks like. Notice how the trunk of the tree is in clear view, with no other nearby tree trunks in the frame. Our app does it's best to identify the tree trunk in the image so that we can predict the species or genus, but the more of the image that is filled by the tree trunk the better.",
      },
      {
        title: 'Image Quality',
        body: "It is also helpful to upload as high resolution as possible up to 2000x4000 pixels. Our training images were around this quality, and images will be resized in order to capture the same spatial patterns as the training images. Low resolution photos, despite the resizing, tend to get less accurate prediction results.",
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
        title: 'Busy Pictures With Multiple Trees',
        body: "One thing to avoid when taking pictures to upload, is taking pictures with several trees and no clear main subject. If there is no clear main subject in the image, then there is a chance that the tree that will be classified is not the one you are wanting to be classified. To avoid this, try to have one clear main tree in the middle of the frame, and if any other trees are in the picture make sure they are clearly in the background.",
        image: bad_example_busy,
      },
      {
        title: 'Trees That Are Too Small',
        body: "Another thing to avoid when taking pictures to upload, is taking pictures from too far away or of the whole tree. Remember, our app only uses the trunk of the tree to classify its species or genus. Therefore, to maximize the probability of a correct classification, try to take a close up picture of just the trunk of the tree, where the width of the tree is as close to the full width of the picture as possible.",
        image: bad_example_size,
      },
    ]
  },
  {
    title: 'Phone Classification Toggles and What They Do',
    sections: [
      {
        title: 'Species and Genus Toggle',
        body: "The species and genus toggle is used so that the user can choose the level of classification. When the toggle is to the left, the tree will be classified by species. When the toggle is to the right, the uploaded image will be classified by genus.",
        image: toggle_genus,
      },
      {
        title: 'Full and Partial Toggle',
        body: "The full and partial toggle is used for when users want a more accurate classification, however, this comes at the cost of a minimized subset of classes. When the toggle is to the left, it is set to full, and images will be classified against our full library of species or genus. When the toggle is to the right, it is set to partial, and uploaded images will have a higher likelihood of correct classification ONLY if the species or genus exists in the 'partial' subset.",
        image: toggle_partial,
      },
    ]
  }
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
  // {
  //   label: 'PHONE',
  //   link: '/upload/phone',
  //   icon: phone_icon_green
  // },
  {
    label: 'Image Upload',
    link: '/upload/drone/RGB',
    icon: drone_icon_green
  },
  {
    label: 'Coord-based Capture',
    link: '/upload/satellite',
    icon: satellite_icon_green
  },
]

export const aboutKorotuSections = [
  {
    title: '',
    body: "Korotu Technology was founded by Sean and Agata Rudd who bring more than 35 years experience in technology, finance and sustainability in North America, Europe and Asia Pacific.",
    image: ''
  },
  {
    title: '',
    body: "Founder and CEO Sean is an experienced financial technology leader, whose career includes over fifteen years at Accenture leading business and technology strategy in financial services and as global head of payments strategy. He has also worked extensively in the software sector with both startups and established leaders in product management, engineering and client service. Originally from New Zealand, he has a lifelong passion for the outdoors.",
    image: ''
  },
  {
    title: '',
    body: "Co-Founder Agata is a sustainability advocate and a social entrepreneur. She is a founder of Toronto's first reusable takeout container program, a former board member for the Alternatives Journal, and a development manager for the Escarpment Biosphere Conservancy (largest Ontario focused land trust). She worked to tackle educational inequalities in the UK and in a series of corporate HR roles at Grant Thornton and the Financial Conduct Authority. She's a passionate cycling advocate, capoeirista, hiker, camper and whatever else allows her to make the most of the outdoors with Sean and their toddler.",
    image: ''
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
  // {
  //   label: 'SEGMENTATION',
  //   link: '/upload/drone/seg',
  //   icon: tree_icon
  // },
  // {
  //   label: 'LiDAR CLASSIFICATION',
  //   link: '/upload/drone/lidar',
  //   icon: lidar_icon
  // },
]

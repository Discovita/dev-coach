/**
 * Image sizes returned by the backend VersatileImageField serializer.
 * All sizes are generated on-demand and cached in S3.
 */
export interface ImageSizes {
    /** Full-size original image URL */
    original: string;
    /** 100x100 square thumbnail URL */
    thumbnail: string;
    /** 300x169 medium size URL (16:9 aspect ratio) */
    medium: string;
    /** 600x338 large size URL (16:9 aspect ratio) */
    large: string;
  }
  
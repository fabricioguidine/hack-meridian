export interface EventMetadata {
  name: string;
  description: string;
  image_ipfs: string;
}

export interface Event extends EventMetadata {
  /** 32-byte event id in hex (64 chars). */
  id: string;
}

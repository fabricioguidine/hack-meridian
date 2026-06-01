import {
  isConnected,
  requestAccess,
  getAddress,
  signTransaction,
} from "@stellar/freighter-api";
import { config } from "./config";

export async function freighterInstalled(): Promise<boolean> {
  const res = await isConnected();
  return res.isConnected === true;
}

/** Prompts the user to connect Freighter and returns the public key. */
export async function connect(): Promise<string> {
  const res = await requestAccess();
  if (res.error) throw new Error(res.error);
  return res.address;
}

/** Returns the currently authorized address, or null if none. */
export async function currentAddress(): Promise<string | null> {
  const res = await getAddress();
  if (res.error || !res.address) return null;
  return res.address;
}

/** Signs a transaction XDR with Freighter and returns the signed XDR. */
export async function signXDR(xdr: string, address: string): Promise<string> {
  const res = await signTransaction(xdr, {
    networkPassphrase: config.networkPassphrase,
    address,
  });
  if (res.error) throw new Error(String(res.error));
  return res.signedTxXdr;
}

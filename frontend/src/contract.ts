import {
  Address,
  Contract,
  nativeToScVal,
  rpc,
  Transaction,
  TransactionBuilder,
  xdr,
} from "@stellar/stellar-sdk";
import { Buffer } from "buffer";

import { config } from "./config";
import { hexToBytes } from "./util";
import { signXDR } from "./wallet";

const server = new rpc.Server(config.rpcUrl, {
  allowHttp: config.rpcUrl.startsWith("http://"),
});

async function invoke(
  source: string,
  method: string,
  args: xdr.ScVal[],
): Promise<string> {
  if (!config.contractId) throw new Error("VITE_CONTRACT_ID is not set");

  const account = await server.getAccount(source);
  const contract = new Contract(config.contractId);
  const tx = new TransactionBuilder(account, {
    fee: "1000000",
    networkPassphrase: config.networkPassphrase,
  })
    .addOperation(contract.call(method, ...args))
    .setTimeout(60)
    .build();

  const prepared = await server.prepareTransaction(tx);
  const signedXdr = await signXDR(prepared.toXDR(), source);
  const signed = TransactionBuilder.fromXDR(
    signedXdr,
    config.networkPassphrase,
  ) as Transaction;

  const sent = await server.sendTransaction(signed);
  if (sent.status === "ERROR") {
    throw new Error(`submit failed: ${JSON.stringify(sent.errorResult)}`);
  }
  return sent.hash;
}

function idScVal(idHex: string): xdr.ScVal {
  return xdr.ScVal.scvBytes(Buffer.from(hexToBytes(idHex)));
}

export function createEvent(
  organizer: string,
  idHex: string,
  name: string,
  description: string,
  imageIpfs: string,
): Promise<string> {
  return invoke(organizer, "create_event", [
    idScVal(idHex),
    new Address(organizer).toScVal(),
    nativeToScVal(name, { type: "string" }),
    nativeToScVal(description, { type: "string" }),
    nativeToScVal(imageIpfs, { type: "string" }),
  ]);
}

export function mintBadge(
  organizer: string,
  idHex: string,
  recipient: string,
): Promise<string> {
  return invoke(organizer, "mint_badge", [
    idScVal(idHex),
    new Address(recipient).toScVal(),
  ]);
}

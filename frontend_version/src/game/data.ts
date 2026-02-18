import type { AssetBundle, CatDataFile, GameData, TeaDataFile } from './types';

export async function loadGameData(): Promise<GameData & AssetBundle> {
  const [teasResponse, catsResponse, spritesResponse] = await Promise.all([
    fetch('/data/teas_data.json'),
    fetch('/data/cats_data.json'),
    fetch('/data/sprites_config.json'),
  ]);

  if (!teasResponse.ok) {
    throw new Error(`Failed to load teas_data.json (${teasResponse.status})`);
  }

  if (!catsResponse.ok) {
    throw new Error(`Failed to load cats_data.json (${catsResponse.status})`);
  }

  if (!spritesResponse.ok) {
    throw new Error(`Failed to load sprites_config.json (${spritesResponse.status})`);
  }

  const teasFile = (await teasResponse.json()) as TeaDataFile;
  const catsFile = (await catsResponse.json()) as CatDataFile;
  const sprites = (await spritesResponse.json()) as AssetBundle['sprites'];

  return {
    teas: teasFile.teas,
    cats: catsFile.cats,
    sprites,
  };
}
import { CATEGORY_ICON_MAP } from "@/constants/icon-map";

import { FaUser } from "react-icons/fa";

export const getIdentityCategoryIcon = (category: string) => {
    const normalizedCategory = category.toLowerCase();
    if (CATEGORY_ICON_MAP[normalizedCategory]) {
      return CATEGORY_ICON_MAP[normalizedCategory];
    }
    for (const [key, icon] of Object.entries(CATEGORY_ICON_MAP)) {
      if (
        normalizedCategory.includes(key.split("_")[0]) ||
        key.split("_").some((part) => normalizedCategory.includes(part))
      ) {
        return icon;
      }
    }
    return FaUser;
  };
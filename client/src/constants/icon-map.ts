import { AiOutlineSun } from "react-icons/ai";
import { BsStars } from "react-icons/bs";
import {
	FaDollarSign,
	FaDumbbell,
	FaHeart,
	FaPiggyBank,
	FaRegCheckSquare,
	FaUser,
} from "react-icons/fa";
import { MdFamilyRestroom } from "react-icons/md";

export const CATEGORY_ICON_MAP: Record<
	string,
	React.ComponentType<{ className?: string }>
> = {
	passions_and_talents: BsStars,
	maker_of_money: FaDollarSign,
	keeper_of_money: FaPiggyBank,
	spiritual: AiOutlineSun,
	personal_appearance: FaUser,
	physical_expression: FaDumbbell,
	familial_relations: MdFamilyRestroom,
	romantic_relation: FaHeart,
	doer_of_things: FaRegCheckSquare,
};

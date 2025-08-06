using System;
using System.Linq;

namespace Son_topish_oyini
{
	class Program
	{		
		public static int KompyuterSonTopishi(int[] sonlar)
		{
			
			Random rand=new Random();
			
			int tanlanganSon=sonlar.OrderBy(x=>rand.Next()).First();
			return tanlanganSon;
		}
		
		public static int KompyuterSonOylashi(int[] sonlar)
		{
			Random rand=new Random();
			
			int oylanganSon=sonlar.OrderBy(x=>rand.Next()).First();
			return oylanganSon;
		}
		
		public static void Main(string[] args)
		{
			x:Console.Write("Bu son topish o'yini \n O'yinni boshlash uchun 1 sonini yuboring: ");
			int boshlash=int.Parse(Console.ReadLine());
			if(boshlash!=1)
			{
				goto x;
			}
			int[] sonlar={1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
			
			Console.Write("Men 1 dan 10 gacha son o'yladim, topib ko'ringchi: ");
			
			bool takrorlash=true;
			while(takrorlash)
			{
				int i=1;
				int oylanganSon=KompyuterSonOylashi(sonlar);
				y:int urinish=int.Parse(Console.ReadLine());
				if(urinish==oylanganSon)
				{
					Console.WriteLine("Topdingiz! men "+urinish+" ni o'ylagan edim");
					Console.WriteLine(i+" ta urinishda topdingiz!");
					takrorlash=false;
				}
				else if(urinish>oylanganSon)
				{
					Console.Write("Topa olmadingiz! men o'ylagan son bundan kichkina\nQaytadan urinib ko'ring: ");
					i+=1;
					goto y;
				}
				else if(urinish<oylanganSon)
				{
					Console.Write("Topa olmadingiz! men o'ylagan son bundan katta\nQaytadan urinib ko'ring: ");
					i+=1;
					goto y;
				}	
			}
			Console.Write("Endi siz son o'ylang! Tayyor bo'lsangiz 1 ni yuboring:");
			boshlash=int.Parse(Console.ReadLine());
			string javob;
			
			takrorlash=true;
			int j=sonlar.Length-1, k=1;
			while(takrorlash)
			{
				int i=0;
				int tanlanganSon=KompyuterSonTopishi(sonlar);
				Console.Write("Siz o'ylagan son: "+tanlanganSon+"\nAgar to'g'ri bo'lsa ha deb yozing,\nAgar katta bo'lsa '+',\nkichik bo'lsa '-' yozing: ");
				javob=Convert.ToString(Console.ReadLine());
				if(javob.ToLower()=="ha")
				{
					Console.WriteLine(k+" ta urinishda topdim!");
					takrorlash=false;
				}
				
				else if(javob=="+")
				{
					k=k+1;
					i=tanlanganSon;
				}
				
				else if(javob=="-")
				{
					k=k+1;
					j=tanlanganSon-2;
				}
			}
			Console.ReadKey(true);
		}
	}
}
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Semaphore
{
    class Program
    {
        static int minersCount = 5;
        static int coalLeft = 2000;
        static int warehouse = 0;
        static int vehicleCapacity = 200;
        static int mineTime = 10;
        static int unloadTime = 10;
        static int transportTime = 10000;

        static SemaphoreSlim mineSemaphore = new SemaphoreSlim(2, 2);
        static SemaphoreSlim warehouseSemaphore = new SemaphoreSlim(1, 1);
        static object lockObject = new object();

        static string[] minerStatus;

        static void Main(string[] args)
        {
            minerStatus = new string[minersCount];
            Task[] miners = new Task[minersCount];

            Task displayTask = Task.Run(DisplayStatus);

            for (int i = 0; i < minersCount; i++)
            {
                int id = i + 1;
                miners[i] = Task.Run(() => Miner(id));
            }

            Task.WaitAll(miners);
            Console.SetCursorPosition(0, minersCount + 5);
            Console.WriteLine($"\nPozostalo: {coalLeft}, w magazynie: {warehouse}");
        }

        static void Miner(int id)
        {
            while (true)
            {
                mineSemaphore.Wait();
                int mined = 0;

                lock (lockObject)
                {
                    if (coalLeft <= 0)
                    {
                        mineSemaphore.Release();
                        minerStatus[id - 1] = "Zakonczyl prace";
                        break;
                    }

                    mined = Math.Min(vehicleCapacity, coalLeft);
                    coalLeft -= mined;
                    minerStatus[id - 1] = "Wydobywa wegiel";
                }

                for (int i = 0; i < mined; i++)
                    Thread.Sleep(mineTime);

                mineSemaphore.Release();

                minerStatus[id - 1] = "Transportuje wegiel do magazynu";
                Thread.Sleep(transportTime);

                warehouseSemaphore.Wait();
                minerStatus[id - 1] = "Rozladowuje wegiel";

                for (int i = 0; i < mined; i++)
                    Thread.Sleep(unloadTime);

                lock (lockObject)
                {
                    warehouse += mined;
                }

                warehouseSemaphore.Release();
            }
        }

        static void DisplayStatus()
        {
            while (true)
            {
                lock (lockObject)
                {
                    Console.SetCursorPosition(0, 0);
                    Console.WriteLine($"Stan zloza: {coalLeft} jednostek wegla".PadRight(50));
                    Console.WriteLine($"Stan magazynu: {warehouse} jednostek wegla".PadRight(50));
                    Console.WriteLine();

                    for (int i = 0; i < minersCount; i++)
                    {
                        Console.WriteLine($"Gornik {i + 1}: {minerStatus[i]}".PadRight(50));
                    }
                }

                Thread.Sleep(500);

                bool allDone = true;
                foreach (var status in minerStatus)
                {
                    if (status != "Zakonczyl prace")
                    {
                        allDone = false;
                        break;
                    }
                }

            }
        }
    }
}

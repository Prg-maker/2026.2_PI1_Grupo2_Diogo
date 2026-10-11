export function RelatorioPage() {
    return(
        <main className="flex-1 overflow-y-auto px-4 pb-4 pt-34 text-slate-200 sm:p-12">


            <header className="">
                <h1 className="text-2xl font-semibold text-slate-100">Relatórios</h1>
                <span className="text-sm text-slate-400">
                    Geração de relatórios em PDF por execução
                </span>
            </header>
            
            <div  className="w-full h-full mt-5 flex bg-red-400 gap-[20px]">

                
                <div className="h-[532px] w-full max-w-max-[400px] bg-[#0B1628] border border-[#1D293D]/60 rounded-[12px] px-[10px]" >
                    <p> Selecionar Execução</p>

                    <div className="hover:bg-[#00B8DB]/10 transition cursor-pointer flex rounded-lg">
                        <div className="w-2 h-2 bg-[#00D492] rounded-full mt-1"/>

                        
                        <div className="text-[12px] flex flex-col" >
                            <span className="">#0014</span>
                            <span>Labirinto · Flood Fill v2</span>
                            <span>15 de set 2025</span>
                        </div>
                    </div>
                </div>

               <div className="w-full flex flex-col gap-4 ">
                 <div className="h-[390px] w-full bg-[#0B1628] border border-[#1D293D]/60 rounded-[12px]" >
                    a
                </div>

                <div className="h-[126px] w-full bg-[#0B1628] border border-[#1D293D]/60 rounded-[12px]" >
                    a
                </div>
               </div>

                
            </div>

        </main>
    )
}